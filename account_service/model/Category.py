"""
文件名: Category.py
作者: yangchunhui
创建日期: 2026/2/14
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/14
描述: 账单类目模型，定义类目表结构和字段

修改历史:
2026/2/14 - yangchunhui - 初始版本

依赖:
- SQLAlchemy: ORM 框架
- BaseDBModel: 基础数据库模型类

字段说明:
    - name: 类目名称（如"三餐"、"社交"、"零食"、"工资"等）
    - category_type: 类型（1-支出, 2-收入）
    - user_id: 关联用户ID（为空表示系统预设类目，有值表示用户自定义类目）
    - is_system: 是否系统预设类目
    - icon: 图标标识
    - sort_order: 排序顺序
"""

from sqlalchemy import String, Column, Boolean, Integer, BigInteger, Index, SmallInteger

from common.model.BaseDBModel import BaseDBModel


class Category(BaseDBModel):
    __tablename__ = "category"
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_category_type', 'category_type'),
        Index('idx_is_system', 'is_system'),
    )

    # 基本信息
    name = Column(String(50), nullable=False, comment="类目名称")
    category_type = Column(SmallInteger, nullable=False, comment="类型: 1-支出, 2-收入")

    # 关联信息
    user_id = Column(BigInteger, nullable=True, comment="关联用户ID（为空表示系统预设类目）")

    # 属性信息
    is_system = Column(Boolean, default=False, comment="是否系统预设类目")
    icon = Column(String(100), nullable=True, comment="图标标识")
    sort_order = Column(Integer, default=0, comment="排序顺序，数字越小越靠前")
