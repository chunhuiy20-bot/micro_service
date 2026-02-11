from account_service.repository.UserRepository import UserRepository
from account_service.schemas.request.UserRequestSchemas import UserRegisterRequest
from account_service.strategy.RegisterStrategy import RegisterStrategyFactory
from account_service.model.User import User
from common.schemas.CommonResult import Result
from common.utils.decorators.AsyncDecorators import async_retry
from common.utils.decorators.WithRepoDecorators import with_repo
from common.utils.security.PasswordHasher import password_hasher


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
    async def register_user(self, user_repo: UserRepository, user_register_request: UserRegisterRequest) -> Result[bool]:
        """
        方法说明: 用户注册业务逻辑（使用策略模式，有且仅有一种注册方式）
        作者: yangchunhui
        创建时间: 2026/2/10
        修改历史:
        2026/2/10 - yangchunhui - 初始版本
        2026/2/11 - yangchunhui - 重构为策略模式，符合OCP原则
        """
        # 1. 获取注册策略（有且仅有一个）
        strategy = RegisterStrategyFactory.get_strategy(user_register_request)

        # 2. 执行唯一性验证
        error_msg = await strategy.validate_unique(user_repo, user_register_request)
        if error_msg:
            return Result.fail(error_msg)

        # 3. 生成账号
        account = strategy.generate_account(user_register_request)

        # 4. 如果生成的账号已存在，添加后缀确保唯一性
        if not user_register_request.account:
            base_account = account
            counter = 1
            while True:
                wrapper = user_repo.query_wrapper().eq("account", account)
                if not await user_repo.get_one(wrapper):
                    break
                account = f"{base_account}_{counter}"
                counter += 1

        # 5. 密码加密
        hashed_password = password_hasher.hash_password(user_register_request.password)

        # 6. 创建用户对象
        new_user = User(
            account=account,
            password=hashed_password,
            name=user_register_request.name or account,
            email=user_register_request.email,
            phone=user_register_request.phone,
            email_verified=False,
            phone_verified=False,
            status="active"
        )

        # 7. 保存到数据库
        try:
            await user_repo.save(new_user)
            return Result.success(True, message=f"注册成功，注册方式: {strategy.get_register_type()}")
        except Exception as e:
            return Result.fail(f"注册失败: {str(e)}")

    @async_retry(max_retries=3,delay=3)
    @with_repo(UserRepository, db_name="main")
    async def get_email_register_verify_code(self, user_repo: UserRepository, email: str) -> Result[bool]:
        pass



user_service = UserService()
