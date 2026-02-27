from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from stock_service.config.ServiceConfig import stock_service_config
from common.utils.db.mysql.AsyncBaseRepository import AsyncBaseRepository
from stock_service.model.HotSectorChainLinkNews import HotSectorChainLinkNews
from common.utils.db.mysql.MultiAsyncDBManager import multi_db


class HotSectorChainLinkNewsRepository(AsyncBaseRepository[HotSectorChainLinkNews]):
    """产业链环节新闻数据访问层"""

    def __init__(self, db: Optional[AsyncSession] = None, db_name: Optional[str] = None):
        db_url = stock_service_config.mysql_config_async
        multi_db.add_database("main", db_url)
        super().__init__(db, HotSectorChainLinkNews, db_name)


hot_sector_chain_link_news_repo = HotSectorChainLinkNewsRepository(db_name="main")