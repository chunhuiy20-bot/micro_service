"""
文件名: LoginStrategy.py
作者: yangchunhui
创建日期: 2026/2/12
描述: 用户登录策略模式实现

修改历史:
2026/2/12 - yangchunhui - 初始版本
2026/2/12 - yangchunhui - 添加验证码登录策略
"""

from abc import ABC, abstractmethod
from typing import Optional
import re
from account_service.repository.UserRepository import UserRepository
from account_service.model.User import User
from common.utils.security.PasswordHasher import password_hasher
from common.utils.db.redis.AsyncRedisClient import AsyncRedisClient


class LoginStrategy(ABC):
    """登录策略抽象基类"""

    @abstractmethod
    def validate_format(self, identifier: str) -> bool:
        """
        验证标识符格式

        Args:
            identifier: 登录标识符（账号/邮箱/手机号）

        Returns:
            bool: 格式是否正确
        """
        pass

    @abstractmethod
    async def find_user(self, user_repo: UserRepository, identifier: str) -> Optional[User]:
        """
        根据标识符查找用户

        Args:
            user_repo: 用户仓储
            identifier: 登录标识符

        Returns:
            Optional[User]: 用户对象，不存在返回 None
        """
        pass

    @abstractmethod
    def get_login_type(self) -> str:
        """
        获取登录类型标识

        Returns:
            str: 登录类型
        """
        pass

    def requires_password(self) -> bool:
        """
        是否需要密码验证

        Returns:
            bool: 是否需要密码
        """
        return True

    def requires_verify_code(self) -> bool:
        """
        是否需要验证码验证

        Returns:
            bool: 是否需要验证码
        """
        return False

    async def authenticate(
        self,
        user_repo: UserRepository,
        identifier: str,
        password: Optional[str] = None,
        verify_code: Optional[str] = None,
        redis_client: Optional[AsyncRedisClient] = None
    ) -> tuple[bool, Optional[str], Optional[User]]:
        """
        执行认证流程（模板方法）

        Args:
            user_repo: 用户仓储
            identifier: 登录标识符
            password: 密码（密码登录需要）
            verify_code: 验证码（验证码登录需要）
            redis_client: Redis 客户端（验证码登录需要）

        Returns:
            tuple[bool, Optional[str], Optional[User]]: (是否成功, 错误信息, 用户对象)
        """
        # 1. 验证格式
        if not self.validate_format(identifier):
            return False, f"{self.get_login_type()}格式不正确", None

        # 2. 查找用户
        user = await self.find_user(user_repo, identifier)
        if not user:
            return False, f"{self.get_login_type()}不存在", None

        # 3. 检查账号状态
        if user.status != "active":
            return False, f"账号状态异常: {user.status}", None

        # 4. 验证密码或验证码
        if self.requires_password():
            if not password:
                return False, "密码不能为空", None
            if not password_hasher.verify_password(password, user.password):
                return False, "密码错误", None

        if self.requires_verify_code():
            if not verify_code:
                return False, "验证码不能为空", None
            if not redis_client:
                return False, "系统错误：缺少 Redis 客户端", None

            # 验证验证码
            redis_key = self.get_redis_key(identifier)
            stored_code = await redis_client.async_get(redis_key)

            if not stored_code:
                return False, "验证码已过期或不存在，请重新获取", None

            if stored_code != verify_code:
                return False, "验证码错误", None

            # 验证成功后删除验证码（一次性使用）
            await redis_client.async_delete(redis_key)

        return True, None, user

    def get_redis_key(self, identifier: str) -> str:
        """
        获取验证码的 Redis key（验证码登录需要重写）

        Args:
            identifier: 标识符

        Returns:
            str: Redis key
        """
        return ""


class AccountLoginStrategy(LoginStrategy):
    """账号登录策略"""

    def validate_format(self, identifier: str) -> bool:
        """验证账号格式：字母、数字、下划线"""
        return bool(re.match(r'^[a-zA-Z0-9_]+$', identifier))

    async def find_user(self, user_repo: UserRepository, identifier: str) -> Optional[User]:
        """根据账号查找用户"""
        wrapper = user_repo.query_wrapper().eq("account", identifier)
        return await user_repo.get_one(wrapper)

    def get_login_type(self) -> str:
        return "账号"


class EmailLoginStrategy(LoginStrategy):
    """邮箱登录策略"""

    def validate_format(self, identifier: str) -> bool:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, identifier))

    async def find_user(self, user_repo: UserRepository, identifier: str) -> Optional[User]:
        """根据邮箱查找用户"""
        wrapper = user_repo.query_wrapper().eq("email", identifier)
        return await user_repo.get_one(wrapper)

    def get_login_type(self) -> str:
        return "邮箱"


class PhoneLoginStrategy(LoginStrategy):
    """手机号登录策略"""

    def validate_format(self, identifier: str) -> bool:
        """验证手机号格式"""
        phone_pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(phone_pattern, identifier))

    async def find_user(self, user_repo: UserRepository, identifier: str) -> Optional[User]:
        """根据手机号查找用户"""
        wrapper = user_repo.query_wrapper().eq("phone", identifier)
        return await user_repo.get_one(wrapper)

    def get_login_type(self) -> str:
        return "手机号"


class EmailVerifyCodeLoginStrategy(LoginStrategy):
    """邮箱验证码登录策略"""

    def validate_format(self, identifier: str) -> bool:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, identifier))

    async def find_user(self, user_repo: UserRepository, identifier: str) -> Optional[User]:
        """根据邮箱查找用户"""
        wrapper = user_repo.query_wrapper().eq("email", identifier)
        return await user_repo.get_one(wrapper)

    def get_login_type(self) -> str:
        return "邮箱验证码"

    def requires_password(self) -> bool:
        """不需要密码"""
        return False

    def requires_verify_code(self) -> bool:
        """需要验证码"""
        return True

    def get_redis_key(self, identifier: str) -> str:
        """获取邮箱验证码的 Redis key"""
        return f"email_login_verify:{identifier}"


class SmsVerifyCodeLoginStrategy(LoginStrategy):
    """短信验证码登录策略"""

    def validate_format(self, identifier: str) -> bool:
        """验证手机号格式"""
        phone_pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(phone_pattern, identifier))

    async def find_user(self, user_repo: UserRepository, identifier: str) -> Optional[User]:
        """根据手机号查找用户"""
        wrapper = user_repo.query_wrapper().eq("phone", identifier)
        return await user_repo.get_one(wrapper)

    def get_login_type(self) -> str:
        return "短信验证码"

    def requires_password(self) -> bool:
        """不需要密码"""
        return False

    def requires_verify_code(self) -> bool:
        """需要验证码"""
        return True

    def get_redis_key(self, identifier: str) -> str:
        """获取短信验证码的 Redis key"""
        return f"sms_login_verify:{identifier}"


class LoginStrategyFactory:
    """登录策略工厂"""

    @staticmethod
    def get_strategy(identifier: str) -> LoginStrategy:
        """
        根据标识符自动识别登录策略（密码登录）

        Args:
            identifier: 登录标识符（账号/邮箱/手机号）

        Returns:
            LoginStrategy: 登录策略

        Raises:
            ValueError: 无法识别标识符类型
        """
        # 判断是邮箱、手机号还是账号
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^1[3-9]\d{9}$'

        if re.match(email_pattern, identifier):
            return EmailLoginStrategy()
        elif re.match(phone_pattern, identifier):
            return PhoneLoginStrategy()
        else:
            # 默认按账号处理
            return AccountLoginStrategy()

    @staticmethod
    def get_verify_code_strategy(identifier: str) -> LoginStrategy:
        """
        根据标识符获取验证码登录策略

        Args:
            identifier: 登录标识符（邮箱/手机号）

        Returns:
            LoginStrategy: 验证码登录策略

        Raises:
            ValueError: 无法识别标识符类型
        """
        # 判断是邮箱还是手机号
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^1[3-9]\d{9}$'

        if re.match(email_pattern, identifier):
            return EmailVerifyCodeLoginStrategy()
        elif re.match(phone_pattern, identifier):
            return SmsVerifyCodeLoginStrategy()
        else:
            raise ValueError("验证码登录仅支持邮箱或手机号")
