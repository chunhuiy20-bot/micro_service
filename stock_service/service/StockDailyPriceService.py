from typing import List, Optional
from datetime import date
from common.schemas.CommonResult import Result
from common.utils.decorators.AsyncDecorators import async_retry
from common.utils.decorators.WithRepoDecorators import with_repo
from stock_service.model.StockDailyPrice import StockDailyPrice
from stock_service.repository.StockDailyPriceRepository import StockDailyPriceRepository
from stock_service.schemas.request.StockDailyPriceRequestSchemas import StockDailyPriceSaveRequest
from stock_service.schemas.response.StockDailyPriceResponseSchemas import StockDailyPriceResponse


class StockDailyPriceService:

    @async_retry(max_retries=3, delay=3)
    @with_repo(StockDailyPriceRepository, db_name="main")
    async def save(self, repo: StockDailyPriceRepository, request: StockDailyPriceSaveRequest) -> Result[StockDailyPriceResponse]:
        """保存一条日线数据，已存在则更新"""
        wrapper = repo.query_wrapper().eq("symbol", request.symbol).eq("trade_date", request.trade_date)
        existing = await repo.get_one(wrapper)

        try:
            if existing:
                updates = request.model_dump(exclude_none=True)
                updates.pop("symbol", None)
                updates.pop("trade_date", None)
                await repo.update_by_id_selective(existing.id, updates)
                updated = await repo.get_by_id(existing.id)
                return Result.success(StockDailyPriceResponse.model_validate(updated))
            else:
                record = StockDailyPrice(
                    symbol=request.symbol,
                    trade_date=request.trade_date,
                    open=request.open,
                    close=request.close,
                    high=request.high,
                    low=request.low,
                    volume=request.volume,
                    source=request.source,
                )
                saved = await repo.save(record)
                return Result.success(StockDailyPriceResponse.model_validate(saved))
        except Exception as e:
            return Result.fail(f"保存日线数据失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(StockDailyPriceRepository, db_name="main")
    async def list_by_symbol(self, repo: StockDailyPriceRepository, symbol: str,
                             start_date: Optional[date] = None, end_date: Optional[date] = None) -> Result[List[StockDailyPriceResponse]]:
        """查询某只股票的历史日线数据"""
        wrapper = repo.query_wrapper().eq("symbol", symbol).order_by_asc("trade_date")
        if start_date:
            wrapper = wrapper.gte("trade_date", start_date)
        if end_date:
            wrapper = wrapper.lte("trade_date", end_date)
        records = await repo.list(wrapper)
        return Result.success([StockDailyPriceResponse.model_validate(r) for r in records])

    @async_retry(max_retries=3, delay=3)
    @with_repo(StockDailyPriceRepository, db_name="main")
    async def delete_by_symbol(self, repo: StockDailyPriceRepository, symbol: str) -> Result[bool]:
        """删除某只股票的全部日线数据"""
        wrapper = repo.query_wrapper().eq("symbol", symbol)
        records = await repo.list(wrapper)
        if not records:
            return Result.fail(f"股票 '{symbol}' 无历史数据")
        try:
            for r in records:
                await repo.remove_by_id(r.id)
            return Result.success(True)
        except Exception as e:
            return Result.fail(f"删除失败: {str(e)}")


stock_daily_price_service = StockDailyPriceService()
