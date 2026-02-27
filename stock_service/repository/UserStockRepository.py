"""
文件名: UserStockRepository.py
描述: 用户自选股票数据访问层

使用示例:
# 直接使用（无事务）
stocks = await user_stock_repo.list()

# 使用事务
async with UserStockRepository(db_name="main") as repo:
    stock = await repo.save(new_stock)
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from stock_service.config.ServiceConfig import stock_service_config
from common.utils.db.mysql.AsyncBaseRepository import AsyncBaseRepository
from stock_service.model.UserStock import UserStock
from common.utils.db.mysql.MultiAsyncDBManager import multi_db


class UserStockRepository(AsyncBaseRepository[UserStock]):
    """用户自选股票数据访问层"""

    def __init__(self, db: Optional[AsyncSession] = None, db_name: Optional[str] = None):
        db_url = stock_service_config.mysql_config_async
        multi_db.add_database("main", db_url)
        super().__init__(db, UserStock, db_name)


user_stock_repo = UserStockRepository(db_name="main")
