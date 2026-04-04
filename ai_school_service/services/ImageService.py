import uuid
from pathlib import Path
from google import genai
from google.genai import types
from typing import Optional
from ai_school_service.config.AISchoolConfig import ai_school_config


class ImageService:
    _FIX_CODE_PROMPT = """你之前生成的 matplotlib 代码执行失败，请修复代码。
        错误信息:
        {error}
        原代码:
        {code}
        请只返回修复后的完整 Python 代码，不要包含任何 markdown 标记或解释。
    """

    def __init__(self):
        base_url = ai_school_config.openai_base_url.rstrip('/v1')
        self.gemini_client = genai.Client(
            api_key=ai_school_config.openai_api_key,
            http_options=types.HttpOptions(base_url=base_url)
        )
        self.openai_client = ai_school_config.get_openai_client()
        self.image_dir = Path(__file__).resolve().parent.parent / "logs" / "images"
        self.image_dir.mkdir(parents=True, exist_ok=True)
        print(f"ImageService 图片保存目录: {self.image_dir}")

    async def generate_image(self, prompt: str, img_type: str = 'gemini') -> Optional[str]:
        """生成图片并保存到本地，返回文件路径"""
        if img_type == 'matplotlib':
            return await self._generate_matplotlib_image(prompt)
        else:
            return await self._generate_gemini_image(prompt)

    async def _generate_matplotlib_image(self, description: str) -> Optional[str]:
        """生成 matplotlib 图片，最多重试5次"""
        print(f"图片生成调用 matplotlib:{description}")
        code_prompt = f"""生成 matplotlib 代码来绘制：{description}

            要求：
            1. 必须显式 import 所有用到的库（如 import numpy as np, import matplotlib.pyplot as plt 等）
            2. 使用 Agg 后端（无 GUI）
            3. 代码最后必须调用 plt.savefig(filepath) 保存图片，其中 filepath 是一个已定义的变量，不要自己定义文件名
            4. 不要使用 plt.show()
            5. 只返回纯 Python 代码，不要 markdown 标记

            示例：
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import numpy as np
            # ... 你的绘图代码 ...
            plt.savefig(filepath)
            # 使用传入的 filepath 变量
        """

        messages = [
            {"role": "system", "content": "你是一个Python matplotlib专家，生成高质量的绘图代码。"},
            {"role": "user", "content": code_prompt}
        ]

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        code = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": code})

        # 最多尝试10次
        for attempt in range(10):
            try:
                # 清理 markdown 标记
                clean_code = code
                if clean_code.startswith("```python"):
                    clean_code = clean_code[9:]
                if clean_code.startswith("```"):
                    clean_code = clean_code[3:]
                if clean_code.endswith("```"):
                    clean_code = clean_code[:-3]
                clean_code = clean_code.strip()

                # 检查代码中是否有硬编码的文件名，如果有则替换
                import re
                if re.search(r'savefig\(["\'][^"\']+\.png["\']\)', clean_code):
                    print("警告: 代码中包含硬编码文件名，尝试替换为filepath变量")
                    clean_code = re.sub(r'savefig\(["\'][^"\']+\.png["\']\)', 'savefig(filepath)', clean_code)

                filepath = self.image_dir / f"{uuid.uuid4()}.png"
                namespace = {"filepath": str(filepath)}
                print(f"matplotlib 尝试保存到: {filepath}")

                exec(f"import matplotlib\nmatplotlib.use('Agg')\n{clean_code}", namespace)

                if filepath.exists():
                    print(f"{attempt}次尝试后，matplotlib 成功生成: {filepath}")
                    # 关闭所有图形以释放内存
                    exec("import matplotlib.pyplot as plt\nplt.close('all')", namespace)
                    return str(filepath)
                else:
                    raise Exception(f"代码执行后未生成文件，预期路径: {filepath}")

            except Exception as e:
                # 失败时也要关闭图形以释放内存
                try:
                    exec("import matplotlib.pyplot as plt\nplt.close('all')", {})
                except:
                    pass
                print(f"尝试 {attempt + 1}/10 失败: {e}")
                if attempt == 9:
                    print("matplotlib 10次均失败，使用 Gemini 兜底")
                    result = await self._generate_gemini_image(description)
                    if not result:
                        raise Exception("matplotlib 和 Gemini 均失败")
                    return result

                # 请求修复代码
                try:
                    messages.append({"role": "user", "content": self._FIX_CODE_PROMPT.format(error=str(e), code=code)})
                    fix_response = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                    )
                    code = fix_response.choices[0].message.content.strip()
                    messages.append({"role": "assistant", "content": code})
                except Exception as fix_err:
                    print(f"请求修复代码失败: {fix_err}")

        return None

    async def _generate_gemini_image(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """使用 Gemini 生成图片，支持重试"""
        print(f"图片生成调用 Gemini生成图片:{prompt}")
        last_error = None
        import os

        # 记录当前工作目录中的png文件
        cwd = os.getcwd()
        before_files = set(f for f in os.listdir(cwd) if f.endswith('.png'))

        for attempt in range(max_retries):
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-3-pro-image-preview:generateContent",
                    contents=prompt
                )
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'inline_data'):
                            filepath = self.image_dir / f"{uuid.uuid4()}.png"
                            print(f"Gemini 尝试保存到: {filepath}")
                            filepath.write_bytes(part.inline_data.data)
                            print(f"Gemini成功生成图片: {filepath}")

                            # 清理工作目录中新生成的png文件
                            after_files = set(f for f in os.listdir(cwd) if f.endswith('.png'))
                            new_files = after_files - before_files
                            for f in new_files:
                                try:
                                    os.remove(os.path.join(cwd, f))
                                    print(f"清理临时文件: {f}")
                                except:
                                    pass

                            return str(filepath)

                return None
            except Exception as e:
                last_error = e
                print(f"Gemini 尝试 {attempt + 1}/{max_retries} 失败: {e}")

        raise Exception(f"Gemini {max_retries}次均失败: {last_error}")
