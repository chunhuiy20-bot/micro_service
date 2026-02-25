"""
文件名: ExchangeRate.py
作者: yangchunhui
创建日期: 2026/2/15
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/15
描述: 汇率模型，定义货币汇率表结构和字段（单向汇率设计）

修改历史:
2026/2/15 - yangchunhui - 初始版本

依赖:
- SQLAlchemy: ORM 框架
- BaseDBModel: 基础数据库模型类

字段说明:
    - base_currency: 基准货币（如USD）
    - target_currency: 目标货币（如CNY）
    - rate: 汇率（1 base_currency = rate target_currency）
    - source: 汇率来源（如"央行"、"API"等）
    - effective_time: 汇率生效时间

注意：
    - 采用单向汇率设计，反向汇率通过 1/rate 计算
    - 例如：存储 USD->CNY rate=7.25，则 CNY->USD = 1/7.25 = 0.138
"""

from sqlalchemy import String, Column, Index, DECIMAL, DateTime
from datetime import datetime

from common.model.BaseDBModel import BaseDBModel


class ExchangeRate(BaseDBModel):
    __tablename__ = "exchange_rate"
    __table_args__ = (
        Index('idx_base_target', 'base_currency', 'target_currency'),
        Index('idx_effective_time', 'effective_time'),
    )

    # 货币信息
    base_currency = Column(String(10), nullable=False, comment="基准货币（如USD）")
    target_currency = Column(String(10), nullable=False, comment="目标货币（如CNY）")

    # 汇率信息
    rate = Column(DECIMAL(20, 8), nullable=False, comment="汇率（1 base_currency = rate target_currency）")
    source = Column(String(50), nullable=True, comment="汇率来源（如'央行'、'API'）")
    effective_time = Column(DateTime, nullable=False, default=datetime.now, comment="汇率生效时间")
