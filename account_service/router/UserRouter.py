"""
文件名: UserRouter.py
作者: yangchunhui
创建日期: 2026/2/6
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/6 14:41
描述: TODO: 添加文件描述

修改历史:
2026/2/6 14:41 - yangchunhui - 初始版本

依赖:
TODO: 列出主要依赖

使用示例:
TODO: 添加使用示例
"""
from pydantic import BaseModel

from account_service.repository.UserRepository import user_repo
from common.utils.router.CustomRouter import CustomAPIRouter

router = CustomAPIRouter(
    prefix="/api/ai/user",
    tags=["用户服务相关API"],
    auto_log=True,
    logger_name="nutril_plan_api",
    log_exclude_args=["password", "token", "secret", "api_key"]
)


class RequestModel(BaseModel):
    name: str
    password: str


@router.post("/get_user_list", summary="获取用户列表")
async def get_user_list(user: RequestModel):
    user_list = await user_repo.list()
    return {"data": user_list, "code": 200, "message": "success"}
