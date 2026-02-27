"""
文件名: HotSectorStockRepository.py
描述: 热门板块个股数据访问层

使用示例:
# 直接使用（无事务）
stocks = await hot_sector_stock_repo.list()

# 使用事务
async with HotSectorStockRepository(db_name="main") as repo:
    stock = await repo.save(new_stock)
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from stock_service.config.ServiceConfig import stock_service_config
from common.utils.db.mysql.AsyncBaseRepository import AsyncBaseRepository
from stock_service.model.HotSectorStock import HotSectorStock
from common.utils.db.mysql.MultiAsyncDBManager import multi_db


class HotSectorStockRepository(AsyncBaseRepository[HotSectorStock]):
    """热门板块个股数据访问层"""

    def __init__(self, db: Optional[AsyncSession] = None, db_name: Optional[str] = None):
        db_url = stock_service_config.mysql_config_async
        multi_db.add_database("main", db_url)
        super().__init__(db, HotSectorStock, db_name)


hot_sector_stock_repo = HotSectorStockRepository(db_name="main")
