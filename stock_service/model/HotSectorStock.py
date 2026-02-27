from sqlalchemy import String, Column, BigInteger, Numeric, Text, Index
from common.model.BaseDBModel import BaseDBModel



class HotSectorStock(BaseDBModel):
    """
    热门板块个股表
    每个产业链环节下的代表性个股
    """
    __tablename__ = "hot_sector_stock"
    __table_args__ = (
        Index('idx_chain_link_id', 'chain_link_id'),
        Index('idx_symbol', 'symbol'),
    )

    chain_link_id = Column(BigInteger, nullable=False, comment="关联 hot_sector_chain_link.id")
    symbol = Column(String(20), nullable=False, comment="股票代码，如 NVDA")
    name = Column(String(50), nullable=True, comment="股票简称，如 英伟达")
    reason = Column(Text, nullable=True, comment="入选理由或该股在板块中的核心竞争力")
    momentum_score = Column(Numeric(5, 2), nullable=True, comment="个股动能评分 0-100")
