from typing import Optional
from pydantic import BaseModel, Field


class UserStockAddRequest(BaseModel):
    symbol: str = Field(..., description="股票代码，如 AAPL / 300750.SZ / 0700.HK")
    name: Optional[str] = Field(None, description="股票名称")
    exchange: Optional[str] = Field(None, description="交易所，如 NASDAQ / SZ / SS / HKEX")
    source: Optional[str] = Field("yfinance", description="默认数据源: yfinance / alpha_vantage / twelve_data")
    sort_order: Optional[str] = Field("0", description="排序权重")


class UserStockUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="股票名称")
    exchange: Optional[str] = Field(None, description="交易所")
    source: Optional[str] = Field(None, description="默认数据源")
    sort_order: Optional[str] = Field(None, description="排序权重")
