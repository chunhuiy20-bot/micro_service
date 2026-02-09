from account_service.model.User import User
from account_service.repository.UserRepository import UserRepository
from common.schemas.CommonResult import Result
from common.utils.decorators.AsyncDecorators import async_retry
from common.utils.decorators.WithRepoDecorators import with_repo


class UserService:

    def __init__(self):
        pass

    @async_retry(max_retries=3,delay=3)
    @with_repo(UserRepository, db_name="main")
    async def get_user_list(self, user_repo: UserRepository) -> Result[list]:
        user_list = await user_repo.list()
        return Result.success(user_list, include_timestamp=True)


    @async_retry(max_retries=3,delay=3)
    @with_repo(UserRepository, db_name="main")
    async def register_user(self, user_repo: UserRepository) -> Result[bool]:
        pass




user_service = UserService()
