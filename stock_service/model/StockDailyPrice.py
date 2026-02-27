from sqlalchemy import String, Column, BigInteger, Date, Numeric, Index, UniqueConstraint
from common.model.BaseDBModel import BaseDBModel


class StockDailyPrice(BaseDBModel):
    """
    股票日线价格表
    每只股票每天一条记录，存储当日 OHLC 数据
    """
    __tablename__ = "stock_daily_price"
    __table_args__ = (
        UniqueConstraint('symbol', 'trade_date', name='uq_symbol_date'),
        Index('idx_symbol', 'symbol'),
        Index('idx_trade_date', 'trade_date'),
    )

    symbol = Column(String(20), nullable=False, comment="股票代码，如 AAPL / 300750.SZ / 0700.HK")
    trade_date = Column(Date, nullable=False, comment="交易日期")
    open = Column(Numeric(12, 4), nullable=True, comment="开盘价")
    close = Column(Numeric(12, 4), nullable=True, comment="收盘价")
    high = Column(Numeric(12, 4), nullable=True, comment="最高价")
    low = Column(Numeric(12, 4), nullable=True, comment="最低价")
    volume = Column(BigInteger, nullable=True, comment="成交量")
    source = Column(String(20), default="yfinance", comment="数据来源: yfinance / alpha_vantage / twelve_data")
