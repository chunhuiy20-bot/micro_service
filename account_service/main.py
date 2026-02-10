from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from account_service.router.UserRouter import router as user_router
from common.utils.exception.GlobalExceptionHandlers import register_exception_handlers
from common.utils.limiter.SlowApiRateLimiter import limiter
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="Logic Gateway")

# 注册限流器到应用
app.state.limiter = limiter

# 注册限流异常处理器
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    限流异常处理器
    当请求超过限流阈值时返回 429 状态码
    """
    return JSONResponse(
        status_code=429,
        content={
            "code": 429,
            "message": "请求过于频繁，请稍后再试",
            "detail": str(exc.detail)
        }
    )


register_exception_handlers(app)
app.include_router(user_router)
