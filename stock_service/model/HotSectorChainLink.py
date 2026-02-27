from sqlalchemy import String, Column, BigInteger, Text, Index
from common.model.BaseDBModel import BaseDBModel


class HotSectorChainLink(BaseDBModel):
    """
    热门板块产业链环节表
    每个板块有上游/中游/下游三条记录
    """
    __tablename__ = "hot_sector_chain_link"
    __table_args__ = (
        Index('idx_sector_id', 'sector_id'),
    )

    sector_id = Column(BigInteger, nullable=False, comment="关联 hot_sector.id")
    chain_type = Column(String(20), nullable=False, comment="环节类型: upstream / midstream / downstream")
    stage = Column(String(50), nullable=True, comment="环节名称，如 上游：设备与材料")
    description = Column(Text, nullable=True, comment="该环节在当前叙事中的作用")
