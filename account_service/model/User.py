from sqlalchemy import String, Column, Boolean, Index

from common.model.BaseDBModel import BaseDBModel


class User(BaseDBModel):
    __tablename__ = "user"
    __table_args__ = (
        Index('idx_account', 'account'),
        Index('idx_email', 'email'),
        Index('idx_phone', 'phone'),
    )

    # 基本信息
    account = Column(String(50), unique=True, nullable=False, comment="登录账号（唯一）")
    name = Column(String(50), nullable=True, comment="用户昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")

    # 登录凭证
    email = Column(String(100), unique=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, nullable=True, comment="手机号")
    password = Column(String(255), nullable=False, comment="密码（加密存储）")

    # 验证状态
    email_verified = Column(Boolean, default=False, comment="邮箱是否已验证")
    phone_verified = Column(Boolean, default=False, comment="手机号是否已验证")

    # 账号状态
    status = Column(String(20), default="active", comment="账号状态: active-正常, disabled-禁用, locked-锁定")