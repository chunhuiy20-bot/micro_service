from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class SectorRiseInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sector_name: str = Field(..., description="板块名称，如：半导体、新能源车")
    rise_pct: Optional[float] = Field(..., description="今日涨幅百分比，如 3.5 表示 3.5%，若无数据则为 null")
    main_reason: str = Field(..., description="今日上涨的主要原因，结合资金面、消息面简要说明")
    catalysts: List[str] = Field(..., description="近期重要政策利好或产业催化事件列表")


class TopRisingSectorsResult(BaseModel):
    """OpenAI 结构化输出包装器"""
    model_config = ConfigDict(extra="forbid")
    date: str = Field(..., description="数据日期，ISO 格式，如 2026-02-27")
    sectors: List[SectorRiseInfo] = Field(..., description="今日涨幅前5板块，按涨幅降序排列")
