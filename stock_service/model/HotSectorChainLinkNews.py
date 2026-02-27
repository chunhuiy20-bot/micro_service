from sqlalchemy import String, Column, BigInteger, Text, Index
from common.model.BaseDBModel import BaseDBModel


class HotSectorChainLinkNews(BaseDBModel):
    """
    产业链环节新闻表
    每个环节对应多条相关新闻
    """
    __tablename__ = "hot_sector_chain_link_news"
    __table_args__ = (
        Index('idx_chain_link_id_news', 'chain_link_id'),
    )

    chain_link_id = Column(BigInteger, nullable=False, comment="关联 hot_sector_chain_link.id")
    title = Column(String(255), nullable=False, comment="新闻标题")
    summary = Column(Text, nullable=True, comment="新闻摘要")
    source_url = Column(String(512), nullable=False, comment="新闻来源链接")