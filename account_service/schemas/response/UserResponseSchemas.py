from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    account: str = Field(..., description="登录账号")
    name: Optional[str] = Field(None, description="用户昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    email_verified: bool = Field(False, description="邮箱是否已验证")
    phone_verified: bool = Field(False, description="手机号是否已验证")
    status: str = Field(..., description="账号状态")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    @field_serializer('id')
    def serialize_id(self, value: int) -> str:
        """将 id 序列化为字符串"""
        return str(value)

    class Config:
        from_attributes = True  # 允许从 ORM 模型创建
