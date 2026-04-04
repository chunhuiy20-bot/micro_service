import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ai_school_service.router.QuestionRouter import router as question_router
from ai_school_service.router.ImageRouter import router as image_router
from ai_school_service.config.AISchoolConfig import ai_school_config
from common.utils.exception.GlobalExceptionHandlers import register_exception_handlers
from common.utils.limiter.SlowApiRateLimiter import limiter
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="AI School Service")

# 注册限流器到应用
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """限流异常处理器"""
    return JSONResponse(
        status_code=429,
        content={
            "code": 429,
            "message": "请求过于频繁，请稍后再试",
            "detail": str(exc.detail)
        }
    )


register_exception_handlers(app)
app.include_router(question_router)
app.include_router(image_router)
