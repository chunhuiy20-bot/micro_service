from pydantic import BaseModel, Field
from typing import List, Optional


class Stock(BaseModel):
    symbol: str = Field(..., description="股票代码，如 NVDA")
    name: str = Field(..., description="股票简称，如 英伟达")
    reason: str = Field(..., description="入选理由或该股在板块中的核心竞争力")
    momentum_score: float = Field(..., description="个股动能评分 0-100")


class ChainLink(BaseModel):
    stage: str = Field(..., description="产业链环节名称，如：上游设备、中游制造、下游终端")
    description: str = Field(..., description="该环节在当前叙事中的作用")
    key_stocks: List[Stock] = Field(..., description="该环节下的代表性个股列表")


class HighMomentumSector(BaseModel):
    sector_name: str = Field(..., description="板块名称，如：AI半导体、低空经济")
    narrative: str = Field(..., description="当前核心上涨叙事/逻辑")
    heat_index: float = Field(..., description="板块热度指数 0-100")

    # 产业链结构
    upstream: ChainLink = Field(..., description="上游环节详情")
    midstream: ChainLink = Field(..., description="中游环节详情")
    downstream: ChainLink = Field(..., description="下游环节详情")

    # 宏观关联
    catalysts: List[str] = Field(..., description="近期催化剂事件列表")
    risk_tips: str = Field(..., description="板块潜在风险提示")


# 使用示例
example_input = {
    "sector_name": "AI半导体",
    "narrative": "算力需求爆发叠加2nm工艺量产预期",
    "heat_index": 95.5,
    "upstream": {
        "stage": "上游：设备与材料",
        "description": "光刻机及高带宽内存(HBM)材料",
        "key_stocks": [
            {"symbol": "ASML", "name": "艾司摩尔", "reason": "EUV光刻机垄断者", "momentum_score": 88},
            {"symbol": "AMAT", "name": "应用材料", "reason": "半导体设备龙头", "momentum_score": 82}
        ]
    },
    "midstream": {
        "stage": "中游：设计与代工",
        "description": "GPU/NPU设计与先进工艺代工",
        "key_stocks": [
            {"symbol": "NVDA", "name": "英伟达", "reason": "AI算力绝对核心", "momentum_score": 98},
            {"symbol": "TSM", "name": "台积电", "reason": "先进封装CoWoS产能支撑", "momentum_score": 92}
        ]
    },
    "downstream": {
        "stage": "下游：应用与终端",
        "description": "AI服务器与大模型厂商",
        "key_stocks": [
            {"symbol": "SMCI", "name": "超微电脑", "reason": "液冷服务器订单爆发", "momentum_score": 95},
            {"symbol": "MSFT", "name": "微软", "reason": "Copilot商业化落地", "momentum_score": 85}
        ]
    },
    "catalysts": ["GTC大会召开", "季度财报超预期"],
    "risk_tips": "估值处于历史高位，关注美联储降息预期变动"
}