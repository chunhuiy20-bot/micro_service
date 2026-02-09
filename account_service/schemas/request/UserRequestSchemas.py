
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserLoginRequest(BaseModel):
    """用户登录请求（支持用户名/邮箱/手机号登录）"""
    account: str = Field(..., description="登录账号（用户名/邮箱/手机号）")
    password: str = Field(..., min_length=6, description="密码")

    @property
    def login_type(self) -> Literal["email", "phone", "username"]:
        """自动识别登录类型"""
        if '@' in self.account:
            return "email"
        elif re.match(r'^1[3-9]\d{9}$', self.account):
            return "phone"
        else:
            return "username"


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="用户昵称")
    account: str = Field(..., min_length=3, max_length=50, description="登录账号（唯一）")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")

    @field_validator('account')
    @classmethod
    def validate_account(cls, v):
        """验证账号格式：只允许字母、数字、下划线"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('账号只能包含字母、数字和下划线')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is not None:
            # 中国大陆手机号验证
            if not re.match(r'^1[3-9]\d{9}$', v):
                raise ValueError('手机号格式不正确')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v
