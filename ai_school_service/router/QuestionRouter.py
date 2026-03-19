"""
文件名: QuestionRouter.py
作者: yangchunhui
创建日期: 2026/3/19
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/3/19
描述: A-Level 题目变体生成路由

修改历史:
2026/3/19 - yangchunhui - 初始版本

依赖:
- fastapi: 路由框架
- ALevelQuestionVariantGenerator: 题目变体生成服务

使用示例:
from ai_school_service.router.QuestionRouter import router as question_router
app.include_router(question_router)
"""

from ai_school_service.schemas.QuestionVariantGenerator import QuestionEntry
from ai_school_service.services.ALevelQuestionVariantGenerator import ALevelQuestionVariantGenerator
from common.utils.router.CustomRouter import CustomAPIRouter

router = CustomAPIRouter(
    prefix="/api/ai-school/question",
    tags=["A-Level 题目变体生成相关API"],
    auto_log=True,
    logger_name="ai-school-service",
)

generator = ALevelQuestionVariantGenerator()


"""
接口说明: 根据原题生成一道相似但不同的 A-Level 变体题目
作者: yangchunhui
创建时间: 2026/3/19
修改历史: 2026/3/19 - yangchunhui - 初始版本
"""
@router.post("/variant", summary="生成 A-Level 题目变体")
async def generate_variant(question: QuestionEntry):
    return await generator.get_question(question)
