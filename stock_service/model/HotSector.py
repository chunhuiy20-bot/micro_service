from sqlalchemy import String, Column, Date, Numeric, Text, Index, UniqueConstraint
from common.model.BaseDBModel import BaseDBModel


class HotSector(BaseDBModel):
    """
    热门板块主表
    每个板块每天一条记录，由 AI 定时爬取写入
    """
    __tablename__ = "hot_sector"
    __table_args__ = (
        UniqueConstraint('sector_name', 'record_date', name='uq_sector_date'),
        Index('idx_record_date', 'record_date'),
    )

    record_date = Column(Date, nullable=False, comment="数据采集日期")
    sector_name = Column(String(50), nullable=False, comment="板块名称，如 AI半导体、低空经济")
    narrative = Column(Text, nullable=True, comment="当前核心上涨叙事/逻辑")
    heat_index = Column(Numeric(5, 2), nullable=True, comment="板块热度指数 0-100")
    catalysts = Column(Text, nullable=True, comment="近期催化剂事件列表，JSON 数组存储")
    risk_tips = Column(Text, nullable=True, comment="板块潜在风险提示")
