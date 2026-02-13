"""
文件名: RegisterStrategy.py
作者: yangchunhui
创建日期: 2026/2/11
描述: 用户注册策略模式实现

修改历史:
2026/2/11 - yangchunhui - 初始版本
2026/2/12 - yangchunhui - 添加验证码发送策略
"""

from abc import ABC, abstractmethod
from typing import Optional
import random
import re
from account_service.repository.UserRepository import UserRepository
from account_service.schemas.request.UserRequestSchemas import UserRegisterRequest
from common.schemas.CommonResult import Result
from common.utils.db.redis.AsyncRedisClient import AsyncRedisClient


class RegisterStrategy(ABC):
    """注册策略抽象基类"""

    @abstractmethod
    async def validate_unique(self, user_repo: UserRepository, request: UserRegisterRequest) -> Optional[str]:
        """
        验证唯一性
        返回: 如果验证失败返回错误信息，成功返回 None
        """
        pass

    @abstractmethod
    def generate_account(self, request: UserRegisterRequest) -> str:
        """生成账号（如果未提供）"""
        pass

    @abstractmethod
    def get_register_type(self) -> str:
        """获取注册类型标识"""
        pass

    @abstractmethod
    def validate_format(self, target: str) -> bool:
        """
        验证目标格式（邮箱或手机号）

        Args:
            target: 目标地址（邮箱或手机号）

        Returns:
            bool: 格式是否正确
        """
        pass

    @abstractmethod
    async def check_target_registered(self, user_repo: UserRepository, target: str) -> bool:
        """
        检查目标是否已注册

        Args:
            user_repo: 用户仓储
            target: 目标地址

        Returns:
            bool: 是否已注册
        """
        pass

    @abstractmethod
    async def send_verify_code(self, target: str, code: str, purpose: str = "register") -> None:
        """
        发送验证码

        Args:
            target: 目标地址
            code: 验证码
            purpose: 用途（register-注册，login-登录）

        Raises:
            Exception: 发送失败时抛出异常
        """
        pass

    @abstractmethod
    def get_redis_key(self, target: str) -> str:
        """
        获取 Redis 存储的 key

        Args:
            target: 目标地址

        Returns:
            str: Redis key
        """
        pass

    @abstractmethod
    def get_success_message(self) -> str:
        """
        获取验证码发送成功消息

        Returns:
            str: 成功消息
        """
        pass

    @staticmethod
    def generate_code() -> str:
        """
        生成6位数字验证码

        Returns:
            str: 验证码
        """
        return str(random.randint(100000, 999999))

    async def send_register_verify_code(
        self,
        user_repo: UserRepository,
        target: str,
        redis_client: AsyncRedisClient
    ) -> Result[bool]:
        """
        发送注册验证码（模板方法）

        Args:
            user_repo: 用户仓储
            target: 目标地址（邮箱或手机号）
            redis_client: Redis 客户端

        Returns:
            Result[bool]: 发送结果
        """
        # 1. 验证格式
        if not self.validate_format(target):
            return Result.fail(f"{self.get_register_type()}格式不正确")

        # 2. 检查是否已注册
        if await self.check_target_registered(user_repo, target):
            return Result.fail(f"该{self.get_register_type()}已被注册")

        # 3. 生成验证码
        verify_code = self.generate_code()

        # 4. 存储到 Redis（5分钟过期）
        redis_key = self.get_redis_key(target)
        try:
            await redis_client.async_set(redis_key, verify_code, ex=300)
        except Exception as e:
            return Result.fail(f"验证码存储失败: {str(e)}")

        # 5. 发送验证码
        try:
            await self.send_verify_code(target, verify_code)
            return Result.success(True, message=self.get_success_message())
        except Exception as e:
            # 发送失败时删除 Redis 中的验证码
            await redis_client.async_delete(redis_key)
            return Result.fail(f"验证码发送失败: {str(e)}")


class AccountRegisterStrategy(RegisterStrategy):
    """账号注册策略"""

    async def validate_unique(self, user_repo: UserRepository, request: UserRegisterRequest) -> Optional[str]:
        wrapper = user_repo.query_wrapper().eq("account", request.account)
        if await user_repo.get_one(wrapper):
            return "账号已存在"
        return None

    def generate_account(self, request: UserRegisterRequest) -> str:
        return request.account

    def get_register_type(self) -> str:
        return "account"

    def validate_format(self, target: str) -> bool:
        """账号注册不需要验证码"""
        return False

    async def check_target_registered(self, user_repo: UserRepository, target: str) -> bool:
        """账号注册不需要验证码"""
        return False

    async def send_verify_code(self, target: str, code: str) -> None:
        """账号注册不需要验证码"""
        raise NotImplementedError("账号注册不支持验证码发送")

    def get_redis_key(self, target: str) -> str:
        """账号注册不需要验证码"""
        return ""

    def get_success_message(self) -> str:
        """账号注册不需要验证码"""
        return ""


class EmailRegisterStrategy(RegisterStrategy):
    """邮箱注册策略"""

    def __init__(self):
        from account_service.config.ServiceConfig import account_service_config
        from common.utils.func.email.BaseEmailSender import BaseEmailSender
        # 在策略内部初始化 email_sender
        self.email_sender = BaseEmailSender(config=account_service_config.get_email_config())

    async def validate_unique(self, user_repo: UserRepository, request: UserRegisterRequest) -> Optional[str]:
        wrapper = user_repo.query_wrapper().eq("email", request.email)
        if await user_repo.get_one(wrapper):
            return "邮箱已被使用"
        return None

    def generate_account(self, request: UserRegisterRequest) -> str:
        """从邮箱生成账号"""
        if request.account:
            return request.account
        return request.email.split('@')[0]

    def get_register_type(self) -> str:
        return "email"

    def validate_format(self, target: str) -> bool:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, target))

    async def check_target_registered(self, user_repo: UserRepository, target: str) -> bool:
        """检查邮箱是否已注册"""
        wrapper = user_repo.query_wrapper().eq("email", target)
        existing_user = await user_repo.get_one(wrapper)
        return existing_user is not None

    async def send_verify_code(self, target: str, code: str, purpose: str = "register") -> None:
        """发送邮箱验证码"""
        if purpose == "login":
            # 登录验证码邮件模板
            email_content = f"""
            <html>
            <body>
                <h2>登录验证</h2>
                <p>您的登录验证码是：<strong style="font-size: 24px; color: #1890ff;">{code}</strong></p>
                <p>验证码有效期为 5 分钟，请尽快完成登录。</p>
                <p>如果这不是您的操作，请立即修改密码以保护账号安全。</p>
            </body>
            </html>
            """
            subject = "登录验证码"
        else:
            # 注册验证码邮件模板
            email_content = f"""
            <html>
            <body>
                <h2>欢迎注册</h2>
                <p>您的邮箱验证码是：<strong style="font-size: 24px; color: #1890ff;">{code}</strong></p>
                <p>验证码有效期为 5 分钟，请尽快完成验证。</p>
                <p>如果这不是您的操作，请忽略此邮件。</p>
            </body>
            </html>
            """
            subject = "邮箱注册验证码"

        await self.email_sender.send_html_email(
            to=target,
            subject=subject,
            html_content=email_content
        )

    def get_redis_key(self, target: str) -> str:
        """获取邮箱验证码的 Redis key"""
        return f"email_register_verify:{target}"

    def get_success_message(self) -> str:
        """获取成功消息"""
        return "验证码已发送，请查收邮件"


class PhoneRegisterStrategy(RegisterStrategy):
    """手机号注册策略"""

    async def validate_unique(self, user_repo: UserRepository, request: UserRegisterRequest) -> Optional[str]:
        wrapper = user_repo.query_wrapper().eq("phone", request.phone)
        if await user_repo.get_one(wrapper):
            return "手机号已被使用"
        return None

    def generate_account(self, request: UserRegisterRequest) -> str:
        """从手机号生成账号"""
        if request.account:
            return request.account
        return f"user_{request.phone[-6:]}"

    def get_register_type(self) -> str:
        return "phone"

    def validate_format(self, target: str) -> bool:
        """验证手机号格式"""
        phone_pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(phone_pattern, target))

    async def check_target_registered(self, user_repo: UserRepository, target: str) -> bool:
        """检查手机号是否已注册"""
        wrapper = user_repo.query_wrapper().eq("phone", target)
        existing_user = await user_repo.get_one(wrapper)
        return existing_user is not None

    async def send_verify_code(self, target: str, code: str, purpose: str = "register") -> None:
        """发送短信验证码（模拟实现）"""
        # 模拟短信发送，实际应该调用短信服务商 API
        if purpose == "login":
            print(f"[短信模拟] 发送登录验证码到手机号: {target}")
            print(f"[短信模拟] 验证码内容: 【系统通知】您的登录验证码是 {code}，5分钟内有效，请勿泄露。")
        else:
            print(f"[短信模拟] 发送注册验证码到手机号: {target}")
            print(f"[短信模拟] 验证码内容: 【系统通知】您的注册验证码是 {code}，5分钟内有效，请勿泄露。")

    def get_redis_key(self, target: str) -> str:
        """获取短信验证码的 Redis key"""
        return f"sms_register_verify:{target}"

    def get_success_message(self) -> str:
        """获取成功消息"""
        return "验证码已发送，请查收短信"


class RegisterStrategyFactory:
    """注册策略工厂"""

    @staticmethod
    def get_strategy(request: UserRegisterRequest) -> RegisterStrategy:
        """
        根据请求获取对应的注册策略（有且仅有一个）
        优先级: account > email > phone
        """
        if request.account:
            return AccountRegisterStrategy()
        elif request.email:
            return EmailRegisterStrategy()
        elif request.phone:
            return PhoneRegisterStrategy()
        else:
            raise ValueError("必须提供一个标识符（account、email 或 phone）")

    @staticmethod
    def get_verify_code_strategy(target: str) -> RegisterStrategy:
        """
        根据目标类型获取验证码发送策略

        Args:
            target: 目标地址（邮箱或手机号）

        Returns:
            RegisterStrategy: 注册策略

        Raises:
            ValueError: 无法识别目标类型
        """
        # 判断是邮箱还是手机号
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^1[3-9]\d{9}$'

        if re.match(email_pattern, target):
            return EmailRegisterStrategy()
        elif re.match(phone_pattern, target):
            return PhoneRegisterStrategy()
        else:
            raise ValueError("无法识别的目标类型，请提供有效的邮箱或手机号")
