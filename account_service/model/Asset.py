"""
文件名: Asset.py
作者: yangchunhui
创建日期: 2026/2/15
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/15
描述: 用户资产模型，定义用户具体资产表结构和字段

修改历史:
2026/2/15 - yangchunhui - 初始版本

依赖:
- SQLAlchemy: ORM 框架
- BaseDBModel: 基础数据库模型类

字段说明:
    - user_id: 关联用户ID
    - asset_category_id: 关联资产大类ID（1-现金, 2-银行卡, 3-股票, 4-加密货币）
    - name: 资产名称（现金:"美元"，银行卡:"工商银行"，股票:"特斯拉"，加密货币:"比特币"）
    - symbol: 交易代码（股票/加密货币用，如TSLA, BTC）
    - account_name: 账户名称（用户自定义，如"我的工资卡"、"零钱包"）
    - account_number: 账号（银行卡号、股票账户号等）
    - card_type: 卡类型（银行卡用，1-借记卡, 2-信用卡）
    - quantity: 持有数量/余额
    - price_currency: 计价货币（如USD, CNY, JPY）
    - current_price: 当前单价（股票/加密货币用）
    - cost_basis: 成本价（股票/加密货币用）
"""

from sqlalchemy import String, Column, BigInteger, Index, DECIMAL, SmallInteger

from common.model.BaseDBModel import BaseDBModel


class Asset(BaseDBModel):
    __tablename__ = "asset"
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_asset_category_id', 'asset_category_id'),
        Index('idx_user_category', 'user_id', 'asset_category_id'),
    )

    # 关联信息
    user_id = Column(BigInteger, nullable=False, comment="关联用户ID")
    asset_category_id = Column(BigInteger, nullable=False, comment="关联资产大类ID")

    # 基本信息
    name = Column(String(100), nullable=False, comment="资产名称")
    symbol = Column(String(20), nullable=True, comment="交易代码（如TSLA, BTC），用于股票和加密货币")
    account_name = Column(String(100), nullable=True, comment="账户名称（用户自定义）")

    # 银行卡相关字段
    account_number = Column(String(100), nullable=True, comment="账号（银行卡号、股票账户号等）")
    card_type = Column(SmallInteger, nullable=True, comment="卡类型: 1-借记卡, 2-信用卡（银行卡用）")

    # 数量和价格信息
    quantity = Column(DECIMAL(20, 8), nullable=False, default=0, comment="持有数量/余额（支持8位小数）")
    price_currency = Column(String(10), nullable=False, comment="计价货币（如USD, CNY, JPY）")
    current_price = Column(DECIMAL(20, 8), nullable=True, comment="当前单价（以price_currency计价），用于股票和加密货币")
    cost_basis = Column(DECIMAL(20, 8), nullable=True, comment="成本价（用于计算收益），用于股票和加密货币")
