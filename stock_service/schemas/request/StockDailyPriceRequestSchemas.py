from typing import Optional
from pydantic import BaseModel, Field
from datetime import date


class StockDailyPriceSaveRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    trade_date: date = Field(..., description="交易日期，格式: 2024-01-01")
    open: Optional[float] = Field(None, description="开盘价")
    close: Optional[float] = Field(None, description="收盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    volume: Optional[int] = Field(None, description="成交量")
    source: Optional[str] = Field("yfinance", description="数据来源")
