"""
文件名: StockDailyPriceRepository.py
描述: 股票日线价格数据访问层

使用示例:
# 直接使用（无事务）
prices = await stock_daily_price_repo.list()

# 使用事务
async with StockDailyPriceRepository(db_name="main") as repo:
    price = await repo.save(new_price)
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from stock_service.config.ServiceConfig import stock_service_config
from common.utils.db.mysql.AsyncBaseRepository import AsyncBaseRepository
from stock_service.model.StockDailyPrice import StockDailyPrice
from common.utils.db.mysql.MultiAsyncDBManager import multi_db


class StockDailyPriceRepository(AsyncBaseRepository[StockDailyPrice]):
    """股票日线价格数据访问层"""

    def __init__(self, db: Optional[AsyncSession] = None, db_name: Optional[str] = None):
        db_url = stock_service_config.mysql_config_async
        multi_db.add_database("main", db_url)
        super().__init__(db, StockDailyPrice, db_name)


stock_daily_price_repo = StockDailyPriceRepository(db_name="main")
