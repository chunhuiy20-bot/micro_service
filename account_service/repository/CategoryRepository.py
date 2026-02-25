"""
文件名: CategoryRepository.py
作者: yangchunhui
创建日期: 2026/2/15
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/15
描述: 类目数据访问层，提供类目相关的数据库操作

修改历史:
2026/2/15 - yangchunhui - 初始版本

依赖:
- AsyncBaseRepository: 异步基础仓储类
- Category: 类目模型
- MultiAsyncDBManager: 多数据库管理器

使用示例:
# 直接使用（无事务）
category_repo = CategoryRepository(db_name="main")
categories = await category_repo.list()

# 使用事务
async with CategoryRepository(db_name="main") as repo:
    category = await repo.save(new_category)

async with self.category_repo:
    category = await repo.save(category)
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from account_service.config.ServiceConfig import account_service_config
from common.utils.db.mysql.AsyncBaseRepository import AsyncBaseRepository
from account_service.model.Category import Category
from common.utils.db.mysql.MultiAsyncDBManager import multi_db


class CategoryRepository(AsyncBaseRepository[Category]):
    """类目数据访问层"""

    def __init__(self, db: Optional[AsyncSession] = None, db_name: Optional[str] = None):
        """
        方法说明: 初始化类目仓储，配置数据库连接
        作者: yangchunhui
        创建时间: 2026/2/15
        修改历史:
        2026/2/15 - yangchunhui - 初始版本
        """
        db_url = account_service_config.mysql_config_async
        multi_db.add_database("main", db_url)
        super().__init__(db, Category, db_name)


# 初始化数据库连接
category_repo = CategoryRepository(db_name="main")
