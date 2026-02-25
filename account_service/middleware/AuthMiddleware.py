"""
文件名: AuthMiddleware.py
作者: yangchunhui
创建日期: 2026/2/25
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/25
描述: JWT 鉴权中间件，拦截所有请求并校验 Token，白名单路径直接放行

修改历史:
2026/2/25 - yangchunhui - 初始版本

依赖:
- fastapi: Web 框架
- JwtHandler: JWT 处理器
- ServiceConfig: 服务配置

使用示例:
app.add_middleware(AuthMiddleware)
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from account_service.config.ServiceConfig import account_service_config
from common.utils.jwt.JwtHandler import JwtHandler, TokenExpiredError, TokenInvalidError

jwt_handler = JwtHandler(account_service_config.get_jwt_config())

# 不需要鉴权的路径（前缀匹配）
WHITELIST = [
    "/api/account/user/login",
    "/api/account/user/register",
    "/api/account/user/login/verify_code",
    "/api/account/user/register/verify_code",
    "/docs",
    "/openapi.json",
    "/health",
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(w) for w in WHITELIST):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"code": 401, "message": "缺少认证 Token"})

        token = auth_header[7:]
        try:
            payload = jwt_handler.decode_token(token)
        except TokenExpiredError:
            return JSONResponse(status_code=401, content={"code": 401, "message": "Token 已过期"})
        except TokenInvalidError:
            return JSONResponse(status_code=401, content={"code": 401, "message": "Token 无效"})

        # 将用户信息注入请求 state，供后续路由使用
        request.state.user_id = payload.sub
        request.state.user_extra = payload.extra

        return await call_next(request)
