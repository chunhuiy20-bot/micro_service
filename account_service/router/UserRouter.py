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

from fastapi import Request
from account_service.schemas.request.UserRequestSchemas import UserRegisterRequest
from account_service.service.UserService import user_service
from common.utils.router.CustomRouter import CustomAPIRouter
from common.utils.limiter.ConcurrencyLimiter import ConcurrencyLimiter

router = CustomAPIRouter(
    prefix="/api/account/user",
    tags=["用户服务相关API"],
    auto_log=True,
    logger_name="account-service",
    log_exclude_args=["password", "token", "secret", "api_key"]
)

# 为每个接口创建独立的并发限制器
register_queue_limiter = ConcurrencyLimiter(max_concurrent=10, timeout=30.0)

"""
接口说明: 创建用户的接口。使用并发限制器，超出限制排队等待,应为使用了一种消耗内内存的hash来做加密，破解方会有极大的成本，但同时我们也要消耗内村，所以先限制并发
作者: yangchunhui
创建时间: 2026/2/10
修改历史: 2026/2/10 - yangchunhui - 初始版本
"""
@router.post("/register_user", summary="创建用户（支持排队）")
@register_queue_limiter  # 使用独立的限制器，最多5个并发
async def register_user_with_queue(request: Request, user: UserRegisterRequest):
    pass
    # 模拟耗时操作
    # await asyncio.sleep(2)
    # return {
    #     "message": "注册成功（排队模式）",
    #     "account": user.account,
    #     "limiter_stats": register_queue_limiter.get_stats()  # 获取这个接口的统计
    # }

