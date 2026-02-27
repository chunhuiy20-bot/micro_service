from datetime import date, timedelta
from typing import List, Optional
from common.schemas.CommonResult import Result
from common.utils.decorators.AsyncDecorators import async_retry
from common.utils.decorators.WithRepoDecorators import with_repo
from stock_service.model.UserStock import UserStock
from stock_service.repository.UserStockRepository import UserStockRepository
from stock_service.schemas.request.UserStockRequestSchemas import UserStockAddRequest, UserStockUpdateRequest
from stock_service.schemas.request.StockDailyPriceRequestSchemas import StockDailyPriceSaveRequest
from stock_service.schemas.response.UserStockResponseSchemas import UserStockResponse
from stock_service.service.StockDailyPriceService import stock_daily_price_service
from stock_service.service.StockService import stock_service


class UserStockService:

    async def _sync_daily_prices(self, symbol: str, source: str):
        """
        同步股票日线数据：无数据则拉取近30天，有数据则补充到今天
        Args:
            symbol:
            source:
        """
        today = date.today()

        existing_result = await stock_daily_price_service.list_by_symbol(symbol)
        if existing_result.data:
            latest_date = max(r.trade_date for r in existing_result.data)
            if latest_date >= today:
                return
            start_date = latest_date + timedelta(days=1)
            klines = stock_service.get_kline(
                symbol, source=source,
                start=start_date.isoformat(),
                end=today.isoformat(),
            )
        else:
            klines = stock_service.get_kline(symbol, source=source, period="1mo")

        for k in klines:
            try:
                trade_date = date.fromisoformat(str(k.get("time", ""))[:10])
            except Exception:
                continue
            req = StockDailyPriceSaveRequest(
                symbol=symbol,
                trade_date=trade_date,
                open=k.get("open"),
                close=k.get("close"),
                high=k.get("high"),
                low=k.get("low"),
                volume=k.get("volume"),
                source=source,
            )
            await stock_daily_price_service.save(req)

    @async_retry(max_retries=3, delay=3)
    @with_repo(UserStockRepository, db_name="main")
    async def add(self, user_stock_repo: UserStockRepository, user_id: int, request: UserStockAddRequest) -> Result[UserStockResponse]:
        """添加自选股票"""
        wrapper = user_stock_repo.query_wrapper().eq("user_id", user_id).eq("symbol", request.symbol)
        if await user_stock_repo.get_one(wrapper):
            return Result.fail(f"股票 '{request.symbol}' 已在自选列表中")

        stock = UserStock(
            user_id=user_id,
            symbol=request.symbol,
            name=request.name,
            exchange=request.exchange,
            source=request.source,
            sort_order=request.sort_order,
        )
        try:
            saved = await user_stock_repo.save(stock)
            await self._sync_daily_prices(request.symbol, request.source or "yfinance")
            return Result.success(UserStockResponse.model_validate(saved))
        except Exception as e:
            return Result.fail(f"添加自选失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(UserStockRepository, db_name="main")
    async def update(self, user_stock_repo: UserStockRepository, user_id: int, stock_id: int, request: UserStockUpdateRequest) -> Result[bool]:
        """修改自选股票信息"""
        stock = await user_stock_repo.get_by_id(stock_id)
        if not stock:
            return Result.fail("自选股票不存在")
        if stock.user_id != user_id:
            return Result.fail("无权限修改该自选股票")

        updates = request.model_dump(exclude_none=True)
        if not updates:
            return Result.fail("没有需要更新的字段")

        try:
            await user_stock_repo.update_by_id_selective(stock_id, updates)
            return Result.success(True)
        except Exception as e:
            return Result.fail(f"修改自选失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(UserStockRepository, db_name="main")
    async def remove(self, user_stock_repo: UserStockRepository, user_id: int, stock_id: int) -> Result[bool]:
        """删除自选股票"""
        stock = await user_stock_repo.get_by_id(stock_id)
        if not stock:
            return Result.fail("自选股票不存在")
        if stock.user_id != user_id:
            return Result.fail("无权限删除该自选股票")

        try:
            await user_stock_repo.remove_by_id(stock_id)
            return Result.success(True)
        except Exception as e:
            return Result.fail(f"删除自选失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(UserStockRepository, db_name="main")
    async def list_by_user(self, user_stock_repo: UserStockRepository, user_id: int) -> Result[List[UserStockResponse]]:
        """查询用户自选列表"""
        wrapper = user_stock_repo.query_wrapper().eq("user_id", user_id).order_by_asc("sort_order")
        stocks = await user_stock_repo.list(wrapper)
        return Result.success([UserStockResponse.model_validate(s) for s in stocks])


user_stock_service = UserStockService()
