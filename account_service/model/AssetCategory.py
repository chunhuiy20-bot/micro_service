"""
文件名: AssetCategory.py
作者: yangchunhui
创建日期: 2026/2/15
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/15
描述: 资产大类模型，定义资产类型表结构和字段

修改历史:
2026/2/15 - yangchunhui - 初始版本

依赖:
- SQLAlchemy: ORM 框架
- BaseDBModel: 基础数据库模型类

字段说明:
    - name: 资产类型名称（如"现金"、"银行卡"、"股票"、"加密货币"）
    - code: 类型代码（如"cash"、"bank"、"stock"、"crypto"）
    - icon: 图标标识
    - sort_order: 排序顺序
"""

from sqlalchemy import String, Column, Integer, Index

from common.model.BaseDBModel import BaseDBModel


class AssetCategory(BaseDBModel):
    __tablename__ = "asset_category"
    __table_args__ = (
        Index('idx_code', 'code'),
    )

    # 基本信息
    name = Column(String(50), nullable=False, comment="资产类型名称")
    code = Column(String(20), nullable=False, unique=True, comment="类型代码")
    icon = Column(String(100), nullable=True, comment="图标标识")
    sort_order = Column(Integer, default=0, comment="排序顺序，数字越小越靠前")
