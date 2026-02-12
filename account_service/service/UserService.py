from account_service.config.ServiceConfig import account_service_config
from account_service.repository.UserRepository import UserRepository
from account_service.schemas.request.UserRequestSchemas import UserRegisterRequest
from account_service.strategy.RegisterStrategy import RegisterStrategyFactory
from account_service.strategy.LoginStrategy import LoginStrategyFactory
from account_service.strategy.VerifyCodeSendStrategy import VerifyCodeSenderFactory
from account_service.model.User import User
from common.schemas.CommonResult import Result
from common.utils.decorators.AsyncDecorators import async_retry
from common.utils.decorators.WithRepoDecorators import with_repo
from common.utils.security.PasswordHasher import password_hasher
from common.utils.db.redis.AsyncRedisClient import AsyncRedisClient
from account_service.schemas.response.UserResponseSchemas import UserResponse

class UserService:

    def __init__(self):
        self.redis_client: AsyncRedisClient = AsyncRedisClient(
            config=account_service_config.get_redis_config()
        )

    @async_retry(max_retries=3,delay=3)
    @with_repo(UserRepository, db_name="main")
    async def get_user_list(self, user_repo: UserRepository) -> Result[list]:
        """
        方法说明: 获取用户列表
        作者: yangchunhui
        创建时间: 2026/2/12
        修改历史:
        2026/2/12 - yangchunhui - 初始版本
        """
        user_list = await user_repo.list()
        # 将 ORM 对象转换为 Pydantic 模型
        user_response_list = [UserResponse.model_validate(user) for user in user_list]
        return Result.success(user_response_list, include_timestamp=True)

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
        2026/2/12 - yangchunhui - 添加验证码校验
        """
        # 1. 获取注册策略（有且仅有一个）
        strategy = RegisterStrategyFactory.get_strategy(user_register_request)

        # 2. 验证码校验（邮箱或手机号注册需要验证码）
        if user_register_request.email or user_register_request.phone:
            target = user_register_request.email or user_register_request.phone
            redis_key = strategy.get_redis_key(target)

            # 从 Redis 获取验证码
            stored_code = await self.redis_client.async_get(redis_key)

            if not stored_code:
                return Result.fail("验证码已过期或不存在，请重新获取")

            if stored_code != user_register_request.verify_code:
                return Result.fail("验证码错误")

            # 验证成功后删除验证码（一次性使用）
            await self.redis_client.async_delete(redis_key)

        # 3. 执行唯一性验证
        error_msg = await strategy.validate_unique(user_repo, user_register_request)
        if error_msg:
            return Result.fail(error_msg)

        # 4. 生成账号
        account = strategy.generate_account(user_register_request)

        # 5. 如果生成的账号已存在，添加后缀确保唯一性
        if not user_register_request.account:
            base_account = account
            counter = 1
            while True:
                wrapper = user_repo.query_wrapper().eq("account", account)
                if not await user_repo.get_one(wrapper):
                    break
                account = f"{base_account}_{counter}"
                counter += 1

        # 6. 密码加密
        hashed_password = password_hasher.hash_password(user_register_request.password)

        # 7. 创建用户对象
        new_user = User(
            account=account,
            password=hashed_password,
            name=user_register_request.name or account,
            email=user_register_request.email,
            phone=user_register_request.phone,
            email_verified=user_register_request.email is not None,  # 通过验证码注册的邮箱已验证
            phone_verified=user_register_request.phone is not None,  # 通过验证码注册的手机已验证
            status="active"
        )

        # 8. 保存到数据库
        try:
            await user_repo.save(new_user)
            return Result.success(True, message=f"注册成功，注册方式: {strategy.get_register_type()}")
        except Exception as e:
            return Result.fail(f"注册失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(UserRepository, db_name="main")
    async def send_register_verify_code(self, user_repo: UserRepository, target: str) -> Result[bool]:
        """
        方法说明: 发送注册验证码（使用验证码发送策略，支持邮箱和手机号）
        作者: yangchunhui
        创建时间: 2026/2/12
        修改历史:
        2026/2/12 - yangchunhui - 初始版本
        2026/2/12 - yangchunhui - 重构为独立的验证码发送策略
        """
        try:
            # 获取验证码发送器
            sender = VerifyCodeSenderFactory.get_sender(target)

            # 发送注册验证码
            return await sender.send_verify_code(
                user_repo=user_repo,
                target=target,
                redis_client=self.redis_client,
                purpose="register",
                check_exists=True
            )
        except ValueError as e:
            return Result.fail(str(e))
        except Exception as e:
            return Result.fail(f"验证码发送失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(UserRepository, db_name="main")
    async def login(self, user_repo: UserRepository, account: str, password: str, login_type: str = "password") -> Result[UserResponse]:
        """
        方法说明: 用户登录（使用策略模式，支持账号/邮箱/手机号登录，支持密码或验证码）
        作者: yangchunhui
        创建时间: 2026/2/12
        修改历史:
        2026/2/12 - yangchunhui - 初始版本
        2026/2/12 - yangchunhui - 统一密码登录和验证码登录
        """
        try:
            # 根据 login_type 选择策略
            if login_type == "verify_code":
                # 验证码登录
                strategy = LoginStrategyFactory.get_verify_code_strategy(account)
                success, error_msg, user = await strategy.authenticate(
                    user_repo=user_repo,
                    identifier=account,
                    verify_code=password,  # 验证码作为 password 传入
                    redis_client=self.redis_client
                )
            else:
                # 密码登录
                strategy = LoginStrategyFactory.get_strategy(account)
                success, error_msg, user = await strategy.authenticate(
                    user_repo=user_repo,
                    identifier=account,
                    password=password
                )

            if not success:
                return Result.fail(error_msg)

            # 转换为响应模型
            user_response = UserResponse.model_validate(user)
            return Result.success(user_response, message=f"登录成功，登录方式: {strategy.get_login_type()}")

        except ValueError as e:
            return Result.fail(str(e))
        except Exception as e:
            return Result.fail(f"登录失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(UserRepository, db_name="main")
    async def send_login_verify_code(self, user_repo: UserRepository, target: str) -> Result[bool]:
        """
        方法说明: 发送登录验证码（使用策略模式，支持邮箱和手机号）
        作者: yangchunhui
        创建时间: 2026/2/12
        修改历史:
        2026/2/12 - yangchunhui - 初始版本
        2026/2/12 - yangchunhui - 重构为独立的验证码发送策略
        """
        try:
            # 获取验证码发送器
            sender = VerifyCodeSenderFactory.get_sender(target)

            # 发送登录验证码
            return await sender.send_verify_code(
                user_repo=user_repo,
                target=target,
                redis_client=self.redis_client,
                purpose="login",
                check_exists=True
            )
        except ValueError as e:
            return Result.fail(str(e))
        except Exception as e:
            return Result.fail(f"验证码发送失败: {str(e)}")



user_service = UserService()
