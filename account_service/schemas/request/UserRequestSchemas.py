
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
import re

class UserLoginRequest(BaseModel):
    """用户登录请求（支持用户名/邮箱/手机号登录，支持密码或验证码）"""
    account: str = Field(..., description="登录账号（用户名/邮箱/手机号）")
    password: str = Field(..., min_length=6, description="密码或验证码")
    login_type: Literal["password", "verify_code"] = Field("password", description="登录类型：password-密码登录，verify_code-验证码登录")

    @property
    def account_type(self) -> Literal["email", "phone", "username"]:
        """自动识别账号类型"""
        if '@' in self.account:
            return "email"
        elif re.match(r'^1[3-9]\d{9}$', self.account):
            return "phone"
        else:
            return "username"


class UserRegisterRequest(BaseModel):
    """用户注册请求（account、email、phone 有且仅有一个）"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="用户昵称")
    account: Optional[str] = Field(None, min_length=3, max_length=50, description="登录账号（唯一）")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    verify_code: Optional[str] = Field(None, min_length=6, max_length=6, description="验证码（邮箱或手机号注册时必填）")

    @field_validator('account')
    @classmethod
    def validate_account(cls, v):
        """验证账号格式：只允许字母、数字、下划线"""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('账号只能包含字母、数字和下划线')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is not None:
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

    @model_validator(mode='after')
    def check_exactly_one_identifier(self):
        """验证有且仅有一个标识符（account、email、phone）"""
        identifiers = [self.account, self.email, self.phone]
        provided_count = sum(1 for x in identifiers if x is not None)

        if provided_count == 0:
            raise ValueError('account、email、phone 必须提供一个')
        elif provided_count > 1:
            raise ValueError('account、email、phone 只能提供一个，不支持多标识符注册')

        # 邮箱或手机号注册时必须提供验证码
        if (self.email or self.phone) and not self.verify_code:
            raise ValueError('邮箱或手机号注册时必须提供验证码')

        # 账号注册不需要验证码
        if self.account and self.verify_code:
            raise ValueError('账号注册不需要验证码')

        return self
