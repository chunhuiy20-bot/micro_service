"""
文件名: ImageRouter.py
作者: yangchunhui
创建日期: 2026/3/27
描述: 图片生成接口，生成图片并上传 OSS 返回 URL
"""

from pydantic import BaseModel, Field
from typing import Optional
from ai_school_service.services.ImageService import ImageService
from ai_school_service.reomte_call.AISchoolServerClient import ai_school_server_client
from common.schemas.CommonResult import Result
from common.utils.router.CustomRouter import CustomAPIRouter

router = CustomAPIRouter(
    prefix="/api/ai-school/image",
    tags=["图片生成相关API"],
    auto_log=True,
    logger_name="ai-school-service",
)

image_service = ImageService()


class ImageGenerateRequest(BaseModel):
    """图片生成请求"""
    prompt: str = Field(..., description="图片描述")
    img_type: str = Field(
        default="matplotlib",
        description="生成类型：'matplotlib'（数学图表/函数/几何/表格）或 'gemini'（复杂情景图）"
    )


@router.post("/generate", summary="生成图片并上传OSS")
async def generate_image(req: ImageGenerateRequest):
    """
    根据 prompt 生成图片，上传到 OSS，返回可访问的 URL。
    """
    # 1. 生成图片到本地
    local_path = await image_service.generate_image(
        prompt=req.prompt,
        img_type=req.img_type
    )
    if not local_path:
        return Result.fail(message="图片生成失败").model_dump()

    # 2. 上传到 OSS
    oss_url = await ai_school_server_client.upload_file(local_path)

    return Result.success(data={"url": oss_url}).model_dump()
