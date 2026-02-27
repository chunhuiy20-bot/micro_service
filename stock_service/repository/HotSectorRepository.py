"""
文件名: HotSectorRepository.py
描述: 热门板块数据访问层

使用示例:
# 直接使用（无事务）
sectors = await hot_sector_repo.list()

# 使用事务
async with HotSectorRepository(db_name="main") as repo:
    sector = await repo.save(new_sector)
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from stock_service.config.ServiceConfig import stock_service_config
from common.utils.db.mysql.AsyncBaseRepository import AsyncBaseRepository
from stock_service.model.HotSector import HotSector
from common.utils.db.mysql.MultiAsyncDBManager import multi_db


class HotSectorRepository(AsyncBaseRepository[HotSector]):
    """热门板块数据访问层"""

    def __init__(self, db: Optional[AsyncSession] = None, db_name: Optional[str] = None):
        db_url = stock_service_config.mysql_config_async
        multi_db.add_database("main", db_url)
        super().__init__(db, HotSector, db_name)


hot_sector_repo = HotSectorRepository(db_name="main")
