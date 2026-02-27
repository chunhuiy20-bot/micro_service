"""
文件名: HotSectorChainLinkRepository.py
描述: 热门板块产业链环节数据访问层

使用示例:
# 直接使用（无事务）
links = await hot_sector_chain_link_repo.list()

# 使用事务
async with HotSectorChainLinkRepository(db_name="main") as repo:
    link = await repo.save(new_link)
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from stock_service.config.ServiceConfig import stock_service_config
from common.utils.db.mysql.AsyncBaseRepository import AsyncBaseRepository
from stock_service.model.HotSectorChainLink import HotSectorChainLink
from common.utils.db.mysql.MultiAsyncDBManager import multi_db


class HotSectorChainLinkRepository(AsyncBaseRepository[HotSectorChainLink]):
    """热门板块产业链环节数据访问层"""

    def __init__(self, db: Optional[AsyncSession] = None, db_name: Optional[str] = None):
        db_url = stock_service_config.mysql_config_async
        multi_db.add_database("main", db_url)
        super().__init__(db, HotSectorChainLink, db_name)


hot_sector_chain_link_repo = HotSectorChainLinkRepository(db_name="main")
