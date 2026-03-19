
from typing import Optional
import subprocess
import uuid
import os
from pathlib import Path
from openai import OpenAI
from ai_school_service.config.AISchoolConfig import ai_school_config
from ai_school_service.schemas.QuestionVariantGenerator import QuestionEntry, QuestionEntryOutPut
from ai_school_service.reomte_call.AISchoolServerClient import ai_school_server_client


class ALevelQuestionVariantGenerator:
    """
    Generate an A Level-style variant question from a source question.
    """

    _SYSTEM_PROMPT = """
        你是一位资深的 A-Level 数学出题专家。你的任务是根据给定的原题，生成一道 相似但不同 的新题目。

        要求：
        1. 新题目必须保持相同的主题（topics）和考察相同的知识点（knowledge_point），保持相近的难度（difficulty）和区分度（discrimination）。
        2. 题目结构（题型、分值分布）应与原题相同。
        3. 所有数学/物理/化学公式必须使用 LaTeX 格式，如 $x ^ 2 + 2x + 1 = 0$。
        4. 修改题目中的具体数值、情境或条件，使其成为全新的题目，而不是简单换数。
        5. 每道小题必须提供正确的参考答案（correctAnswer），解答过程要完整。
        6. 当需要函数图像、几何图形、统计图表，必须设置question_need_image为True，且matplotlib_generate_python_code参数必须填写基于 matplotlib 绘制题目配图的完整 Python 代码。
        7. 你必须只返回纯 JSON，不要包含任何 markdown 标记、解释或多余文字。
        8. parts 里面的 text不要带题号，直接返回题目，不要带有排版符号
        """

    _USER_PROMPT = """
    请根据原题生成一道相识但不相同的题目
    1. 题目主题（topics: {topics} , 考查知识点（knowledge_point: {knowledge_point}
    2. 原题: {origin_question}
    """

    _FIX_CODE_PROMPT = """你之前生成的 matplotlib 代码执行失败，请修复代码。
        错误信息:
        {error}
        原代码:
        {code}    
        请只返回修复后的完整 Python 代码，不要包含任何 markdown 标记或解释。
    """
    _IMAGE_DIR = Path(__file__).resolve().parent.parent / "logs" / "images"

    def __init__(
        self,
        model: str = "gpt-4o",
    ) -> None:
        self.client: OpenAI = ai_school_config.get_openai_client()
        self.model = model



    async def get_question(self, question: QuestionEntry) -> QuestionEntryOutPut:
        # 收集所有小题的知识点
        knowledge_points = ", ".join(part.knowledge_point for part in question.parts)

        user_content = self._USER_PROMPT.format(
            topics=", ".join(question.topics),
            knowledge_point=knowledge_points,
            origin_question=question.model_dump_json(indent=2),
        )

        user_message_content = [
            {"type": "text", "text": user_content},
            {"type": "image_url", "image_url": {"url": question.question_image_url}},
        ]

        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": self._SYSTEM_PROMPT},
                {"role": "user", "content": user_message_content},
            ],
            response_format=QuestionEntryOutPut,
        )
        result: QuestionEntryOutPut = response.choices[0].message.parsed
        print(result)
        if result.question_need_image and result.matplotlib_generate_python_code:
            image_path = self._execute_matplotlib_code_with_retry(result.matplotlib_generate_python_code)
            image_url = await ai_school_server_client.upload_file(image_path)
            result.question_image_url = image_url
        else:
            result.question_image_url = ""

        data = result.model_dump()

        # 删除不需要的字段
        data.pop("question_need_image", None)
        data.pop("matplotlib_generate_python_code", None)
        print(data)

        return data

    def _execute_matplotlib_code_with_retry(self, code: str, max_retries: int = 3) -> str:
        """
        执行 matplotlib 代码，失败时将报错反馈给 AI 修复，最多重试 max_retries 次。
        """
        for attempt in range(max_retries + 1):
            try:
                return self._execute_matplotlib_code(code)
            except RuntimeError as e:
                if attempt >= max_retries:
                    raise
                error_msg = str(e)
                print(f"matplotlib 代码执行失败 (第{attempt + 1}次)，请求 AI 修复...")
                code = self._fix_matplotlib_code(code, error_msg)

    def _fix_matplotlib_code(self, code: str, error: str) -> str:
        """
        将报错信息和原代码发给 AI，让其返回修复后的代码。
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个 Python 代码修复专家，只返回修复后的纯 Python 代码，不要包含任何 markdown 标记或解释。"},
                {"role": "user", "content": self._FIX_CODE_PROMPT.format(error=error, code=code)},
            ],
        )
        fixed_code = response.choices[0].message.content.strip()
        # 去除可能的 markdown 代码块标记
        if fixed_code.startswith("```"):
            fixed_code = fixed_code.split("\n", 1)[1]
            fixed_code = fixed_code.rsplit("```", 1)[0].strip()
        return fixed_code

    @staticmethod
    def _execute_matplotlib_code(code: str) -> str:
        """
        在子进程中执行 AI 生成的 matplotlib 代码，返回生成的图片路径。
        """
        os.makedirs(ALevelQuestionVariantGenerator._IMAGE_DIR, exist_ok=True)
        image_filename = f"{uuid.uuid4().hex}.png"
        image_path = str(ALevelQuestionVariantGenerator._IMAGE_DIR / image_filename)

        # 在代码末尾追加 savefig，确保图片保存到指定路径
        wrapped_code = (
            "import matplotlib\n"
            "matplotlib.use('Agg')\n"
            f"{code}\n"
            "import matplotlib.pyplot as plt\n"
            f"plt.savefig(r'{image_path}', dpi=150, bbox_inches='tight')\n"
            "plt.close()\n"
        )

        proc = subprocess.run(
            ["python", "-c", wrapped_code],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"matplotlib 代码执行失败:\n{proc.stderr}")

        return image_path