from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from datetime import date, datetime


class StockDailyPriceResponse(BaseModel):
    id: int = Field(..., description="ID")
    symbol: str = Field(..., description="股票代码")
    trade_date: date = Field(..., description="交易日期")
    open: Optional[float] = Field(None, description="开盘价")
    close: Optional[float] = Field(None, description="收盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    volume: Optional[int] = Field(None, description="成交量")
    source: Optional[str] = Field(None, description="数据来源")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    @field_serializer('id')
    def serialize_id(self, value: int) -> str:
        return str(value)

    class Config:
        from_attributes = True
