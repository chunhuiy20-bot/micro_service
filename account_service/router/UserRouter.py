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

from fastapi import Query
from account_service.schemas.request.UserRequestSchemas import UserRegisterRequest, UserLoginRequest
from account_service.service.UserService import user_service
from common.utils.router.CustomRouter import CustomAPIRouter
from common.utils.limiter.ConcurrencyLimiter import ConcurrencyLimiter

router = CustomAPIRouter(
    prefix="/api/account/user",
    tags=["记账软件用户服务相关API"],
    auto_log=True,
    logger_name="account-service--2",
    log_exclude_args=["password", "token", "secret", "api_key"]
)

# 为每个接口创建独立的并发限制器
register_queue_limiter = ConcurrencyLimiter(max_concurrent=10, timeout=30.0)
verify_code_limiter = ConcurrencyLimiter(max_concurrent=20, timeout=10.0)

"""
接口说明: 创建用户的接口。使用并发限制器，超出限制排队等待,因为使用了一种消耗内内存的hash来做加密，破解方会有极大的成本，但同时我们也要消耗内村，所以先限制并发
作者: yangchunhui
创建时间: 2026/2/10
修改历史: 2026/2/10 - yangchunhui - 初始版本
"""
@register_queue_limiter  # 使用独立的限制器，最多10个并发
@router.post("/register_user", summary="创建用户（支持排队）")
async def register_user_with_queue(user_register_request: UserRegisterRequest):
    return await user_service.register_user(user_register_request)


"""
接口说明: 获取用户列表
作者: yangchunhui
创建时间: 2026/2/12
修改历史: 2026/2/12 - yangchunhui - 初始版本
"""
@router.get("/list", summary="获取用户列表")
async def get_user_list():
    return await user_service.get_user_list()


"""
接口说明: 用户登录（支持账号/邮箱/手机号登录，支持密码或验证码）
作者: yangchunhui
创建时间: 2026/2/12
修改历史:
2026/2/12 - yangchunhui - 初始版本
2026/2/12 - yangchunhui - 统一密码登录和验证码登录
"""
@router.post("/login", summary="用户登录")
async def login(user_login_request: UserLoginRequest):
    return await user_service.login(
        account=user_login_request.account,
        password=user_login_request.password,
        login_type=user_login_request.login_type
    )


"""
接口说明: 获取登录验证码（支持邮箱和手机号）
作者: yangchunhui
创建时间: 2026/2/12
修改历史: 2026/2/12 - yangchunhui - 初始版本
"""
@verify_code_limiter  # 使用独立的限制器，最多20个并发
@router.get("/login/verify_code", summary="获取登录验证码（邮箱/手机）")
async def get_login_verify_code(
    target: str = Query(..., description="邮箱地址或手机号")
):
    return await user_service.send_login_verify_code(target=target)


"""
接口说明: 获取注册验证码（支持邮箱和手机号）
作者: yangchunhui
创建时间: 2026/2/12
修改历史: 2026/2/12 - yangchunhui - 初始版本
"""
@verify_code_limiter  # 使用独立的限制器，最多20个并发
@router.get("/register/verify_code", summary="获取注册验证码（邮箱/手机）")
async def get_register_verify_code(
    target: str = Query(..., description="邮箱地址或手机号")
):
    return await user_service.send_register_verify_code(target=target)


