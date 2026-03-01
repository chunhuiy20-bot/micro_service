from datetime import date, timedelta
from typing import List, Optional
from common.schemas.CommonResult import Result
from common.utils.decorators.AsyncDecorators import async_retry
from common.utils.decorators.WithRepoDecorators import with_repo
from stock_service.model.UserStock import UserStock
from stock_service.repository.UserStockRepository import UserStockRepository
from stock_service.schemas.request.UserStockRequestSchemas import UserStockAddRequest, UserStockUpdateRequest
from stock_service.schemas.response.UserStockResponseSchemas import UserStockResponse
from stock_service.service.StockDailyPriceService import stock_daily_price_service
from stock_service.service.StockService import stock_service


class UserStockService:

    async def _sync_daily_prices(self, symbol: str, source: str):
        """
        同步股票日线数据：无数据则拉取近1年，有数据则补充到今天。
        按 alpha_vantage → yfinance → twelve_data 顺序自动切换数据源。
        """
        today = date.today()
        one_year_ago = today - timedelta(days=365)

        existing_result = await stock_daily_price_service.list_by_symbol(symbol)
        if existing_result.data:
            latest_date = max(r.trade_date for r in existing_result.data)
            if latest_date >= today:
                return
            start_filter = (latest_date + timedelta(days=1)).isoformat()
        else:
            start_filter = one_year_ago.isoformat()

        # 各数据源拉取参数（tushare 最优先，原生支持 A股）
        source_params = [
            ("tushare", {"interval": "daily", "start_date": start_filter, "end_date": today.isoformat(), "outputsize": 365}),
            ("alpha_vantage", {"interval": "daily", "outputsize": "compact"}),
            ("yfinance", {"interval": "1d", "period": "1y"}),
            ("twelve_data", {"interval": "1day", "start_date": start_filter, "end_date": today.isoformat(), "outputsize": 365}),
        ]

        klines = []
        actual_source = source
        for src, kwargs in source_params:
            try:
                result = stock_service.get_kline(symbol, source=src, **kwargs)
                print(f"[{src}] 拉取结果条数: {len(result)}")
                filtered = [k for k in result if str(k.get("time", ""))[:10] >= start_filter]
                if filtered:
                    klines = filtered
                    actual_source = src
                    break
            except Exception as e:
                print(f"[{src}] 拉取失败: {e}")
                continue

        await stock_daily_price_service.save_batch_klines(klines, symbol=symbol, source=actual_source)
        print(f"[sync] {symbol} 批量保存 {len(klines)} 条日线数据，数据源: {actual_source}")

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
        """查询用户自选列表，附带实时价格"""
        wrapper = user_stock_repo.query_wrapper().eq("user_id", user_id).order_by_asc("sort_order")
        stocks = await user_stock_repo.list(wrapper)
        if not stocks:
            return Result.success([])

        # 按数据源分组，批量拉取实时价格
        source_map: dict[str, list[str]] = {}
        for s in stocks:
            source_map.setdefault(s.source or "yfinance", []).append(s.symbol)

        price_map: dict[str, dict] = {}
        for src, symbols in source_map.items():
            try:
                price_map.update(stock_service.get_realtime_prices(symbols, source=src))
            except Exception:
                pass

        result = []
        for s in stocks:
            resp = UserStockResponse.model_validate(s)
            info = price_map.get(s.symbol, {})
            resp.price = info.get("price")
            resp.open = info.get("open")
            resp.high = info.get("high")
            resp.low = info.get("low")
            resp.volume = info.get("volume")
            cp = info.get("change_percent")
            if isinstance(cp, str):
                cp = float(cp.replace("%", "")) if cp else None
            resp.change_percent = cp
            result.append(resp)
        return Result.success(result)


user_stock_service = UserStockService()
