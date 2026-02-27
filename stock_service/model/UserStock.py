from sqlalchemy import String, Column, BigInteger, Index, UniqueConstraint
from common.model.BaseDBModel import BaseDBModel


class UserStock(BaseDBModel):
    """
    用户自选股票表
    一个用户可以添加多个自选股票，同一用户同一股票代码唯一
    """
    __tablename__ = "user_stock"
    __table_args__ = (
        UniqueConstraint('user_id', 'symbol', name='uq_user_symbol'),
        Index('idx_user_id', 'user_id'),
    )

    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    symbol = Column(String(20), nullable=False, comment="股票代码，如 AAPL / 300750.SZ / 0700.HK")
    name = Column(String(50), nullable=True, comment="股票名称，如 苹果 / 宁德时代")
    exchange = Column(String(20), nullable=True, comment="交易所，如 NASDAQ / SZ / SS / HKEX")
    source = Column(String(20), default="yfinance", comment="默认数据源: yfinance / alpha_vantage / twelve_data")
    sort_order = Column(String(20), default="0", comment="排序权重，数字越小越靠前")
