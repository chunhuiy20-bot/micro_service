from typing import Optional
from datetime import date
from fastapi import Query, Request, HTTPException
from common.utils.router.CustomRouter import CustomAPIRouter
from stock_service.schemas.request.StockDailyPriceRequestSchemas import StockDailyPriceSaveRequest
from stock_service.service.StockDailyPriceService import stock_daily_price_service

router = CustomAPIRouter(
    prefix="/api/stock/daily",
    tags=["股票日线价格"],
    auto_log=True,
    logger_name="stock-service",
)


"""
接口说明: 保存日线数据（存在则更新）
"""
@router.post("/save", summary="保存日线数据")
async def save(request: StockDailyPriceSaveRequest):
    return await stock_daily_price_service.save(request)


"""
接口说明: 查询某只股票历史日线数据
"""
@router.get("/list", summary="查询历史日线数据")
async def list_by_symbol(
    symbol: str = Query(..., description="股票代码"),
    start_date: Optional[date] = Query(None, description="开始日期，格式: 2024-01-01"),
    end_date: Optional[date] = Query(None, description="结束日期，格式: 2024-12-31"),
):
    return await stock_daily_price_service.list_by_symbol(symbol=symbol, start_date=start_date, end_date=end_date)


"""
接口说明: 删除某只股票全部日线数据
"""
@router.post("/{symbol}/delete", summary="删除股票全部日线数据")
async def delete_by_symbol(symbol: str):
    return await stock_daily_price_service.delete_by_symbol(symbol=symbol)
