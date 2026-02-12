"""
文件名: VerifyCodeSendStrategy.py
作者: yangchunhui
创建日期: 2026/2/12
描述: 验证码发送策略（独立复用）

修改历史:
2026/2/12 - yangchunhui - 初始版本
"""

from abc import ABC, abstractmethod
from typing import Optional
import random
import re
from account_service.repository.UserRepository import UserRepository
from common.utils.db.redis.AsyncRedisClient import AsyncRedisClient
from common.schemas.CommonResult import Result


class VerifyCodeSendStrategy(ABC):
    """验证码发送策略抽象基类"""

    @abstractmethod
    def validate_format(self, target: str) -> bool:
        """
        验证目标格式

        Args:
            target: 目标地址（邮箱或手机号）

        Returns:
            bool: 格式是否正确
        """
        pass

    @abstractmethod
    async def send_code(self, target: str, code: str, purpose: str) -> None:
        """
        发送验证码

        Args:
            target: 目标地址
            code: 验证码
            purpose: 用途（register-注册，login-登录，reset_password-重置密码等）

        Raises:
            Exception: 发送失败时抛出异常
        """
        pass

    @abstractmethod
    def get_redis_key(self, target: str, purpose: str) -> str:
        """
        获取 Redis 存储的 key

        Args:
            target: 目标地址
            purpose: 用途

        Returns:
            str: Redis key
        """
        pass

    @abstractmethod
    async def check_target_exists(self, user_repo: UserRepository, target: str) -> bool:
        """
        检查目标是否已注册

        Args:
            user_repo: 用户仓储
            target: 目标地址

        Returns:
            bool: 是否已注册
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

    async def send_verify_code(
        self,
        user_repo: UserRepository,
        target: str,
        redis_client: AsyncRedisClient,
        purpose: str = "register",
        check_exists: bool = True
    ) -> Result[bool]:
        """
        发送验证码（模板方法）

        Args:
            user_repo: 用户仓储
            target: 目标地址
            redis_client: Redis 客户端
            purpose: 用途（register-注册，login-登录）
            check_exists: 是否检查用户存在性（注册时检查不存在，登录时检查存在）

        Returns:
            Result[bool]: 发送结果
        """
        # 1. 验证格式
        if not self.validate_format(target):
            return Result.fail("格式不正确")

        # 2. 检查用户存在性
        exists = await self.check_target_exists(user_repo, target)
        if check_exists:
            if purpose == "register" and exists:
                return Result.fail("该账号已被注册")
            elif purpose == "login" and not exists:
                return Result.fail("该账号未注册")

        # 3. 生成验证码
        verify_code = self.generate_code()

        # 4. 存储到 Redis（5分钟过期）
        redis_key = self.get_redis_key(target, purpose)
        try:
            await redis_client.async_set(redis_key, verify_code, ex=300)
        except Exception as e:
            return Result.fail(f"验证码存储失败: {str(e)}")

        # 5. 发送验证码
        try:
            await self.send_code(target, verify_code, purpose)
            return Result.success(True, message="验证码已发送")
        except Exception as e:
            # 发送失败时删除 Redis 中的验证码
            await redis_client.async_delete(redis_key)
            return Result.fail(f"验证码发送失败: {str(e)}")


class EmailVerifyCodeSender(VerifyCodeSendStrategy):
    """邮箱验证码发送器"""

    def __init__(self):
        from account_service.config.ServiceConfig import account_service_config
        from common.utils.func.email.BaseEmailSender import BaseEmailSender
        # 在策略内部初始化 email_sender
        self.email_sender = BaseEmailSender(config=account_service_config.get_email_config())

    def validate_format(self, target: str) -> bool:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, target))

    async def check_target_exists(self, user_repo: UserRepository, target: str) -> bool:
        """检查邮箱是否已注册"""
        wrapper = user_repo.query_wrapper().eq("email", target)
        existing_user = await user_repo.get_one(wrapper)
        return existing_user is not None

    async def send_code(self, target: str, code: str, purpose: str) -> None:
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

    def get_redis_key(self, target: str, purpose: str) -> str:
        """获取邮箱验证码的 Redis key"""
        return f"email_{purpose}_verify:{target}"


class SmsVerifyCodeSender(VerifyCodeSendStrategy):
    """短信验证码发送器（模拟实现）"""

    def validate_format(self, target: str) -> bool:
        """验证手机号格式"""
        phone_pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(phone_pattern, target))

    async def check_target_exists(self, user_repo: UserRepository, target: str) -> bool:
        """检查手机号是否已注册"""
        wrapper = user_repo.query_wrapper().eq("phone", target)
        existing_user = await user_repo.get_one(wrapper)
        return existing_user is not None

    async def send_code(self, target: str, code: str, purpose: str) -> None:
        """发送短信验证码（模拟实现）"""
        # 模拟短信发送，实际应该调用短信服务商 API
        if purpose == "login":
            print(f"[短信模拟] 发送登录验证码到手机号: {target}")
            print(f"[短信模拟] 验证码内容: 【系统通知】您的登录验证码是 {code}，5分钟内有效，请勿泄露。")
        else:
            print(f"[短信模拟] 发送注册验证码到手机号: {target}")
            print(f"[短信模拟] 验证码内容: 【系统通知】您的注册验证码是 {code}，5分钟内有效，请勿泄露。")

    def get_redis_key(self, target: str, purpose: str) -> str:
        """获取短信验证码的 Redis key"""
        return f"sms_{purpose}_verify:{target}"


class VerifyCodeSenderFactory:
    """验证码发送器工厂"""

    @staticmethod
    def get_sender(target: str) -> VerifyCodeSendStrategy:
        """
        根据目标类型获取验证码发送器

        Args:
            target: 目标地址（邮箱或手机号）

        Returns:
            VerifyCodeSendStrategy: 验证码发送器

        Raises:
            ValueError: 无法识别目标类型
        """
        # 判断是邮箱还是手机号
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^1[3-9]\d{9}$'

        if re.match(email_pattern, target):
            return EmailVerifyCodeSender()
        elif re.match(phone_pattern, target):
            return SmsVerifyCodeSender()
        else:
            raise ValueError("验证码发送仅支持邮箱或手机号")
