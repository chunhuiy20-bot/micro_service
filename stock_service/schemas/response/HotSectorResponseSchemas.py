import json
from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer, model_validator
from datetime import date, datetime


class HotSectorBriefResponse(BaseModel):
    """热门板块基础信息"""
    id: int = Field(..., description="ID")
    record_date: date = Field(..., description="采集日期")
    sector_name: str = Field(..., description="板块名称")
    heat_index: Optional[float] = Field(None, description="热度指数 0-100")
    narrative: Optional[str] = Field(None, description="核心上涨叙事")
    catalysts: Optional[List[str]] = Field(None, description="催化剂事件列表")
    risk_tips: Optional[str] = Field(None, description="风险提示")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    @field_serializer('id')
    def serialize_id(self, value: int) -> str:
        return str(value)

    @model_validator(mode='before')
    @classmethod
    def parse_catalysts(cls, values):
        if hasattr(values, '__dict__'):
            raw = getattr(values, 'catalysts', None)
        else:
            raw = values.get('catalysts')
        if isinstance(raw, str):
            try:
                if hasattr(values, '__dict__'):
                    values.catalysts = json.loads(raw)
                else:
                    values['catalysts'] = json.loads(raw)
            except Exception:
                pass
        return values

    class Config:
        from_attributes = True


class HotSectorStockResponse(BaseModel):
    """板块个股信息"""
    id: int = Field(..., description="ID")
    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票简称")
    reason: Optional[str] = Field(None, description="入选理由")
    momentum_score: Optional[float] = Field(None, description="动能评分 0-100")

    @field_serializer('id')
    def serialize_id(self, value: int) -> str:
        return str(value)

    class Config:
        from_attributes = True


class HotSectorChainLinkResponse(BaseModel):
    """产业链环节信息"""
    id: int = Field(..., description="ID")
    chain_type: str = Field(..., description="环节类型: upstream / midstream / downstream")
    stage: Optional[str] = Field(None, description="环节名称")
    description: Optional[str] = Field(None, description="环节描述")
    key_stocks: List[HotSectorStockResponse] = Field(default_factory=list, description="代表性个股")

    @field_serializer('id')
    def serialize_id(self, value: int) -> str:
        return str(value)

    class Config:
        from_attributes = True


class HotSectorDetailResponse(HotSectorBriefResponse):
    """热门板块详细信息（含产业链）"""
    upstream: Optional[HotSectorChainLinkResponse] = Field(None, description="上游环节")
    midstream: Optional[HotSectorChainLinkResponse] = Field(None, description="中游环节")
    downstream: Optional[HotSectorChainLinkResponse] = Field(None, description="下游环节")
