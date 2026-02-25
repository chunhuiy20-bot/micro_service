"""
文件名: Transaction.py
作者: yangchunhui
创建日期: 2026/2/15
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/15
描述: 流水账单模型，定义交易记录表结构和字段

修改历史:
2026/2/15 - yangchunhui - 初始版本

依赖:
- SQLAlchemy: ORM 框架
- BaseDBModel: 基础数据库模型类

字段说明:
    - user_id: 关联用户ID
    - category_id: 关联类目ID（外键关联到Category表）
    - amount: 交易金额（单位：分，避免浮点数精度问题）
    - transaction_type: 交易类型（1-支出, 2-收入）
    - transaction_date: 交易日期
    - description: 交易描述/备注
    - account_type: 账户类型（1-现金, 2-银行卡, 3-支付宝, 4-微信等）
    - images: 图片附件（JSON格式存储多张图片URL）
    - tags: 标签（JSON格式存储多个标签）
"""

from sqlalchemy import String, Column, BigInteger, Index, SmallInteger, DateTime, Text, DECIMAL
from datetime import datetime

from common.model.BaseDBModel import BaseDBModel


class Transaction(BaseDBModel):
    __tablename__ = "transaction"
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_category_id', 'category_id'),
        Index('idx_transaction_type', 'transaction_type'),
        Index('idx_transaction_date', 'transaction_date'),
        Index('idx_user_date', 'user_id', 'transaction_date'),  # 组合索引，用于按用户查询某时间段的流水
    )

    # 关联信息
    user_id = Column(BigInteger, nullable=False, comment="关联用户ID")
    category_id = Column(BigInteger, nullable=False, comment="关联类目ID")

    # 交易信息
    amount = Column(DECIMAL(15, 2), nullable=False, comment="交易金额（单位：元）")
    transaction_type = Column(SmallInteger, nullable=False, comment="交易类型: 1-支出, 2-收入")
    transaction_date = Column(DateTime, nullable=False, default=datetime.now, comment="交易日期时间")

    # 描述信息
    description = Column(String(200), nullable=True, comment="交易描述/备注")

    # 账户信息
    account_type = Column(SmallInteger, nullable=True, comment="账户类型: 1-现金, 2-银行卡, 3-支付宝, 4-微信, 5-其他")

    # 扩展信息
    images = Column(Text, nullable=True, comment="图片附件（JSON格式）")
    tags = Column(String(500), nullable=True, comment="标签（逗号分隔或JSON格式）")
