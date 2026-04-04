
import asyncio
import uuid
from pathlib import Path
from openai import OpenAI
from ai_school_service.config.AISchoolConfig import ai_school_config
from ai_school_service.schemas.QuestionVariantGenerator import Question, QuestionOutput
from ai_school_service.services.ImageService import ImageService
from ai_school_service.reomte_call.AISchoolServerClient import ai_school_server_client


class ALevelQuestionVariantGenerator:
    """
    Generate an A Level-style variant question from a source question.
    """

    # _SYSTEM_PROMPT = """
    #     你是一位资深的A-Level出题专家。你的任务是根据给定的原题，生成一道相似但不同的新题目。
    #
    #     要求：
    #     1. 新题目必须保持相同的主题（topics）和考察相同的知识点（sub_topics），保持相近但是不必一样的难度（difficulty）和区分度（discrimination）。
    #     2. 题目结构（题型、分值分布）应与原题相同。question_number、topics、sub_topics、source_image_url 保持与原题一致。
    #     3. 所有数学/物理/化学公式必须使用 LaTeX 格式，如 $x ^ 2 + 2x + 1 = 0$。
    #     4. 生成全新的题目，可以改变情境、数值、条件等，只要符合 topics 和 sub_topics 即可。
    #     5. 文科社科题目的数据、案例应合理，不违背常识。
    #     6. 每道小题必须提供正确的参考答案（correctAnswer）。
    #     7. 图片处理规则：
    #        - question 中所有 diagrams 字段必须设置为空列表 []
    #        - 在 stem_materials_need_figures 中描述需要生成的图片，描述的数据必须与你出的新题目一致
    #        - 每个 stem_material 对应一个列表，不需要图片则为空列表 []
    #        - 每张图片用 FigureSpec：{'prompt': '详细描述（包含具体数据）', 'type': 'matplotlib'/'gemini'}
    #        - type='matplotlib': 数学图表/函数图像/几何图形/简单表格
    #        - type='gemini': 仅在 matplotlib 无法处理的复杂情景图时使用
    #     """

    # _USER_PROMPT = """
    # 请根据原题生成一道题目，题目的主题（topics: {topics} , 考查知识点（sub_topics: {sub_topics}
    # 2. 原题: {origin_question}
    # """

    _SYSTEM_PROMPT = """                                                                                                                                                                                                                                                                                                    
      你是一位资深的A-Level出题专家。你的任务是根据给定的考纲知识点，生成一道全新的原创题目。

      要求：          
      1. 新题目必须覆盖相同的 topics 和 sub_topics，难度相近。                                                                                                                                                                                                                                                                
      2. 必须使用全新的情境、背景、数值和设问角度，禁止照搬或微调原题。
         - 换场景：如原题用抛体运动打篮球，新题可以用跳水/发射火箭                                                                                                                                                                                                                                                            
         - 换切入点：如原题正向求解，新题可以逆向推导或加入约束条件                                                                                                                                                                                                                                                           
         - 换数据：所有数值必须重新设计，不能是原题数值的简单倍数或偏移                                                                                                                                                                                                                                                       
      3. 题型和总分值与原题保持一致。                                                                                                                                                                                                                                                                                         
      4. 所有公式使用 LaTeX 格式。                                                                                                                                                                                                                                                                                            
      5. 每道小题必须提供正确的参考答案（correctAnswer）
      6. 题目结构（题型、分值分布）应与原题相同                                                                                                                                                                                                                                                                    
      7. 图片处理规则：
           - question 中所有 diagrams 字段必须设置为空列表 []
           - 在 stem_materials_need_figures 中描述需要生成的图片，描述的数据必须与你出的新题目一致
           - 每个 stem_material 对应一个列表，不需要图片则为空列表 []
           - 每张图片用 FigureSpec：{'prompt': '详细描述（包含具体数据）', 'type': 'matplotlib'/'gemini'}
           - type='matplotlib': 数学图表/函数图像/几何图形/简单表格
           - type='gemini': 仅在 matplotlib 无法处理的复杂情景图时使用                                                                                                                                                                                                                                                                                      
      """

    _USER_PROMPT = """
      考纲信息：                                                                                                                                                                                                                                                                                                              
      - topics: {topics}
      - sub_topics: {sub_topics}                                                                                                                                                                                                                                                                                              
      - 题型与分值结构参考原题

      原题（仅供参考题型结构和难度，禁止复用其情境和数值）：                                                                                                                                                                                                                                                                  
      {origin_question}                                                                                                                                                                                                                                                                                                       

      请生成一道考查相同知识点但情境完全不同的新题，再输出题目。                                                                                                                                                                                                                                
      """

    _IMAGE_DIR = Path(__file__).resolve().parent.parent / "logs" / "images"

    def __init__(
        self,
        model: str = "gpt-4o",
    ) -> None:
        self.client: OpenAI = ai_school_config.get_openai_client()
        self.model = model
        self.image_service = ImageService()



    async def get_question(self, question: Question, num: int = 10) -> list[dict]:
        """并发生成 num 道变体题目，跳过失败的任务"""
        print(f"预计生成: {num}道题目")
        tasks = [self._generate_one(question) for _ in range(num)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, dict)]


    async def _generate_one(self, question: Question) -> dict:
        """生成单道变体题目"""
        try:
            sub_topics = question.sub_topics
            user_content = self._USER_PROMPT.format(
                topics=", ".join(question.topics),
                sub_topics=sub_topics,
                origin_question=question.model_dump_json(indent=2),
            )

            user_message_content = [
                {"type": "text", "text": user_content},
            ]

            # 将题干材料中的图片以多模态方式传入
            for material in question.stem_materials:
                for diagram_url in material.diagrams:
                    user_message_content.append({
                        "type": "image_url",
                        "image_url": {"url": diagram_url},
                    })

            # 将子题中的图片以多模态方式传入
            for sub_q in question.sub_questions:
                for diagram_url in sub_q.diagrams:
                    user_message_content.append({
                        "type": "image_url",
                        "image_url": {"url": diagram_url},
                    })
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT},
                    {"role": "user", "content": user_message_content},
                ],
                response_format=QuestionOutput,
            )

            result: QuestionOutput = response.choices[0].message.parsed

            # 生成并上传图片
            await self._generate_and_upload_images(result)

            return result.question.model_dump()
        except Exception as e:
            print(f"生成失败: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def _generate_and_upload_images(self, output: QuestionOutput):
        """生成并上传图片，更新 URL"""
        for i, prompts in enumerate(output.stem_materials_need_figures):
            if i < len(output.question.stem_materials):
                urls = await self._generate_images(prompts)
                output.question.stem_materials[i].diagrams = urls

    async def _generate_images(self, prompts: list) -> list[str]:
        """根据 prompts 生成图片并上传，返回 URL 列表"""
        urls = []
        for spec in prompts:
            filepath = await self.image_service.generate_image(spec.prompt, spec.type)
            if filepath:
                url = await ai_school_server_client.upload_file(filepath)
                urls.append(url)
        return urls

