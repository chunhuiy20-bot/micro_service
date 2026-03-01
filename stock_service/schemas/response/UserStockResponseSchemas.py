from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime


class UserStockResponse(BaseModel):
    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    exchange: Optional[str] = Field(None, description="交易所")
    source: Optional[str] = Field(None, description="默认数据源")
    sort_order: Optional[str] = Field(None, description="排序权重")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    price: Optional[float] = Field(None, description="实时价格")
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    volume: Optional[int] = Field(None, description="成交量")
    change_percent: Optional[float] = Field(None, description="涨跌幅（%）")

    @field_serializer('id')
    def serialize_id(self, value: int) -> str:
        return str(value)

    @field_serializer('user_id')
    def serialize_user_id(self, value: int) -> str:
        return str(value)

    class Config:
        from_attributes = True
