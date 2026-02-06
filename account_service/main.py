from fastapi import FastAPI
from account_service.router.UserRouter import router as user_router
from common.utils.exception.GlobalExceptionHandlers import register_exception_handlers

app = FastAPI(title="Logic Gateway")

register_exception_handlers(app)
app.include_router(user_router)
