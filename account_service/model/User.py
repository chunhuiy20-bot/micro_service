"""
文件名: User.py
作者: yangchunhui
创建日期: 2026/2/12
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/12
描述: 用户模型，定义用户表结构和字段

修改历史:
2026/2/12 - yangchunhui - 初始版本

依赖:
- SQLAlchemy: ORM 框架
- BaseDBModel: 基础数据库模型类

字段说明:
    - account: 登录账号（唯一）
    - name: 用户昵称
    - avatar: 头像URL
    - email: 邮箱（唯一）
    - phone: 手机号（唯一）
    - password: 密码（加密存储）
    - email_verified: 邮箱是否已验证
    - phone_verified: 手机号是否已验证
    - status: 账号状态（active-正常, disabled-禁用, locked-锁定）
"""

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