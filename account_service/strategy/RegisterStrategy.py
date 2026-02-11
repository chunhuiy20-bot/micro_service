"""
文件名: RegisterStrategy.py
作者: yangchunhui
创建日期: 2026/2/11
描述: 用户注册策略模式实现

修改历史:
2026/2/11 - yangchunhui - 初始版本
"""

from abc import ABC, abstractmethod
from typing import Optional
from account_service.repository.UserRepository import UserRepository
from account_service.schemas.request.UserRequestSchemas import UserRegisterRequest


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


class EmailRegisterStrategy(RegisterStrategy):
    """邮箱注册策略"""

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


class RegisterStrategyFactory:
    """注册策略工厂"""

    _strategies = {
        "account": AccountRegisterStrategy(),
        "email": EmailRegisterStrategy(),
        "phone": PhoneRegisterStrategy(),
    }

    @classmethod
    def get_strategy(cls, request: UserRegisterRequest) -> RegisterStrategy:
        """
        根据请求获取对应的注册策略（有且仅有一个）
        优先级: account > email > phone
        """
        if request.account:
            return cls._strategies["account"]
        elif request.email:
            return cls._strategies["email"]
        elif request.phone:
            return cls._strategies["phone"]
        else:
            raise ValueError("必须提供一个标识符（account、email 或 phone）")
