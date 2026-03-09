import functools
import inspect
from typing import Any, Callable
from fastmcp import Context
from ai_school_mcp.config.ServiceConfig import token_ctx


def require_auth(func: Callable):
    """
    兼容同步和异步 Tool 函数的认证装饰器
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # 1. 提取上下文对象 (FastMCP 自动注入)
        ctx: Context = kwargs.get("ctx")

        if not ctx or not ctx.request_context or not hasattr(ctx.request_context, "request"):
            return {"error": "Authentication failed: Request context not available."}

        # 2. 提取并设置 Token
        try:
            headers = dict(ctx.request_context.request.headers)
            auth_token = headers.get('authorization')
            print(f"auth_token: {auth_token}")

            if not auth_token:
                return {"error": "Missing 'Authorization' header. Please check MCP config."}

            token_ctx.set(auth_token)

        except Exception as e:
            return {"error": f"Auth extraction error: {str(e)}"}

        # 3. 核心兼容逻辑：判断原函数是否需要 await
        if inspect.iscoroutinefunction(func):
            # 如果原函数是 async def
            return await func(*args, **kwargs)
        else:
            # 如果原函数是普通的 def
            return func(*args, **kwargs)

    return wrapper