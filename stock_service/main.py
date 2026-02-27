from fastapi import FastAPI

from common.utils.scheduler.DynamicScheduler import scheduler
from stock_service.router.StockRouter import router as stock_router
from stock_service.router.UserStockRouter import router as user_stock_router
from stock_service.router.StockDailyPriceRouter import router as stock_daily_price_router
from stock_service.router.HotSectorRouter import router as hot_sector_router
from common.utils.exception.GlobalExceptionHandlers import register_exception_handlers
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("FastAPI应用启动，初始化调度器...")
    scheduler.start()

    # scheduler.add_interval_job(
    #     func=custom_task,
    #     seconds=5000,
    #     job_id="custom_task_5s"
    # )

    yield
    # 关闭时
    print("FastAPI应用关闭，停止调度器...")
    scheduler.shutdown()


app = FastAPI(title="Stock Service", lifespan=lifespan)

register_exception_handlers(app)
app.include_router(stock_router)
app.include_router(user_stock_router)
app.include_router(stock_daily_price_router)
app.include_router(hot_sector_router)
