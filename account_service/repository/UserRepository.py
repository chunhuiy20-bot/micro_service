from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.db.AsyncBaseRepository import AsyncBaseRepository
from account_service.model.User import User


class UserRepository(AsyncBaseRepository[User]):
    """用户数据访问层"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
