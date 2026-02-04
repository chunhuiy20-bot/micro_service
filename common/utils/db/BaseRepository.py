"""
BaseRepository - 类似 MyBatis-Plus 的通用 CRUD 基类
提供常用的数据库操作方法，支持链式查询、分页、批量操作等
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc, func
from sqlalchemy.exc import SQLAlchemyError
from common.model.BaseDBModel import BaseDBModel

# 定义泛型类型
T = TypeVar('T', bound=BaseDBModel)


class QueryWrapper:
    """
    建造者模式构建条件包装器
    查询条件包装器，类似 MyBatis-Plus 的 QueryWrapper
    """

    def __init__(self, model_class: Type[BaseDBModel]):
        self.model_class = model_class
        self.conditions = []
        self.order_by_clauses = []
        self._limit = None
        self._offset = None

    def eq(self, field: str, value: Any) -> "QueryWrapper":
        """等于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column == value)
        return self

    def ne(self, field: str, value: Any) -> "QueryWrapper":
        """不等于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column != value)
        return self

    def gt(self, field: str, value: Any) -> "QueryWrapper":
        """大于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column > value)
        return self

    def ge(self, field: str, value: Any) -> "QueryWrapper":
        """大于等于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column >= value)
        return self

    def lt(self, field: str, value: Any) -> "QueryWrapper":
        """小于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column < value)
        return self

    def le(self, field: str, value: Any) -> "QueryWrapper":
        """小于等于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column <= value)
        return self

    def like(self, field: str, value: str) -> "QueryWrapper":
        """模糊查询"""
        if value:
            column = getattr(self.model_class, field)
            self.conditions.append(column.like(f"%{value}%"))
        return self

    def like_left(self, field: str, value: str) -> "QueryWrapper":
        """左模糊查询"""
        if value:
            column = getattr(self.model_class, field)
            self.conditions.append(column.like(f"%{value}"))
        return self

    def like_right(self, field: str, value: str) -> "QueryWrapper":
        """右模糊查询"""
        if value:
            column = getattr(self.model_class, field)
            self.conditions.append(column.like(f"{value}%"))
        return self

    def in_(self, field: str, values: List[Any]) -> "QueryWrapper":
        """IN 查询"""
        if values:
            column = getattr(self.model_class, field)
            self.conditions.append(column.in_(values))
        return self

    def not_in(self, field: str, values: List[Any]) -> "QueryWrapper":
        """NOT IN 查询"""
        if values:
            column = getattr(self.model_class, field)
            self.conditions.append(~column.in_(values))
        return self

    def between(self, field: str, start: Any, end: Any) -> "QueryWrapper":
        """BETWEEN 查询"""
        if start is not None and end is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column.between(start, end))
        return self

    def is_null(self, field: str) -> "QueryWrapper":
        """IS NULL 查询"""
        column = getattr(self.model_class, field)
        self.conditions.append(column.is_(None))
        return self

    def is_not_null(self, field: str) -> "QueryWrapper":
        """IS NOT NULL 查询"""
        column = getattr(self.model_class, field)
        self.conditions.append(column.isnot(None))
        return self

    def order_by_asc(self, *fields: str) -> "QueryWrapper":
        """升序排序"""
        for field in fields:
            column = getattr(self.model_class, field)
            self.order_by_clauses.append(asc(column))
        return self

    def order_by_desc(self, *fields: str) -> "QueryWrapper":
        """降序排序"""
        for field in fields:
            column = getattr(self.model_class, field)
            self.order_by_clauses.append(desc(column))
        return self

    def limit(self, limit: int) -> "QueryWrapper":
        """限制返回数量"""
        self._limit = limit
        return self

    def offset(self, offset: int) -> "QueryWrapper":
        """偏移量"""
        self._offset = offset
        return self

    def build_query(self, query):
        """构建查询"""
        if self.conditions:
            query = query.filter(and_(*self.conditions))
        if self.order_by_clauses:
            query = query.order_by(*self.order_by_clauses)
        if self._offset is not None:
            query = query.offset(self._offset)
        if self._limit is not None:
            query = query.limit(self._limit)
        return query


class BaseRepository(Generic[T]):
    """
    通用 Repository 基类，提供类似 MyBatis-Plus 的 CRUD 操作

    使用示例:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: Session):
                super().__init__(db, User)

        # 使用
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(1)
        users = user_repo.list()
    """

    def __init__(self, db: Session, model_class: Type[T]):
        self.db = db
        self.model_class = model_class

    # ==================== 基础 CRUD 操作 ====================

    def save(self, entity: T) -> T:
        """
        保存实体（新增）

        Args:
            entity: 实体对象

        Returns:
            保存后的实体
        """
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def save_batch(self, entities: List[T]) -> List[T]:
        """
        批量保存

        Args:
            entities: 实体列表

        Returns:
            保存后的实体列表
        """
        try:
            self.db.add_all(entities)
            self.db.commit()
            for entity in entities:
                self.db.refresh(entity)
            return entities
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def update_by_id(self, entity: T) -> bool:
        """
        根据 ID 更新实体

        Args:
            entity: 实体对象（必须包含 id）

        Returns:
            是否更新成功
        """
        try:
            self.db.merge(entity)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def update_by_id_selective(self, id: int, updates: Dict[str, Any]) -> bool:
        """
        根据 ID 选择性更新（只更新非 None 字段）

        Args:
            id: 实体 ID
            updates: 要更新的字段字典

        Returns:
            是否更新成功
        """
        try:
            # 过滤掉 None 值
            updates = {k: v for k, v in updates.items() if v is not None}
            if not updates:
                return False

            result = (
                self.db.query(self.model_class)
                .filter(
                    and_(
                        self.model_class.id == id,
                        self.model_class.del_flag == 0
                    )
                )
                .update(updates)
            )
            self.db.commit()
            return result > 0
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def remove_by_id(self, id: int, physical: bool = False) -> bool:
        """
        根据 ID 删除（默认逻辑删除）

        Args:
            id: 实体 ID
            physical: 是否物理删除，默认 False（逻辑删除）

        Returns:
            是否删除成功
        """
        try:
            if physical:
                # 物理删除
                result = (
                    self.db.query(self.model_class)
                    .filter(
                        and_(
                            self.model_class.id == id
                        )
                    )
                    .delete(synchronize_session=False)
                )
            else:
                # 逻辑删除
                result = (
                    self.db.query(self.model_class)
                    .filter(
                        and_(
                            self.model_class.id == id,
                            self.model_class.del_flag == 0
                        )
                    )
                    .update({"del_flag": 1}, synchronize_session=False)
                )

            self.db.commit()
            return result > 0
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def remove_by_ids(self, ids: List[int], physical: bool = False) -> int:
        """
        根据 ID 列表批量删除

        Args:
            ids: ID 列表
            physical: 是否物理删除

        Returns:
            删除的记录数
        """
        try:
            if physical:
                result = self.db.query(self.model_class).filter(
                    self.model_class.id.in_(ids)
                ).delete(synchronize_session=False)
            else:
                result = (
                    self.db.query(self.model_class)
                    .filter(
                        and_(
                            self.model_class.id.in_(ids),
                            self.model_class.del_flag == 0
                        )
                    )
                    .update({"del_flag": 1}, synchronize_session=False)
                )

            self.db.commit()
            return result
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_by_id(self, id: int) -> Optional[T]:
        """
        根据 ID 查询

        Args:
            id: 实体 ID

        Returns:
            实体对象或 None
        """
        return (
            self.db.query(self.model_class)
            .filter(
                and_(
                    self.model_class.id == id,
                    self.model_class.del_flag == 0
                )
            )
            .first()
        )

    def get_one(self, wrapper: QueryWrapper) -> Optional[T]:
        """
        根据条件查询单个实体

        Args:
            wrapper: 查询条件包装器

        Returns:
            实体对象或 None
        """
        query = (
            self.db.query(self.model_class)
            .filter(
                and_(
                    self.model_class.del_flag == 0
                )
            )
        )
        query = wrapper.build_query(query)
        return query.first()

    def list(self, wrapper: Optional[QueryWrapper] = None) -> List[T]:
        """
        查询列表

        Args:
            wrapper: 查询条件包装器（可选）

        Returns:
            实体列表
        """
        query = (
            self.db.query(self.model_class)
            .filter(
                and_(
                    self.model_class.del_flag == 0
                )
            )
        )
        if wrapper:
            query = wrapper.build_query(query)
        return query.all()

    def list_by_ids(self, ids: List[int]) -> List[T]:
        """
        根据 ID 列表查询

        Args:
            ids: ID 列表

        Returns:
            实体列表
        """
        return (
            self.db.query(self.model_class)
            .filter(
                and_(
                    self.model_class.id.in_(ids),
                    self.model_class.del_flag == 0
                )
            )
            .all()
        )

    def count(self, wrapper: Optional[QueryWrapper] = None) -> int:
        """
        统计数量

        Args:
            wrapper: 查询条件包装器（可选）

        Returns:
            记录数
        """
        query = (
            self.db.query(func.count(self.model_class.id))
            .filter(
                and_(
                    self.model_class.del_flag == 0
                )
            )
        )
        if wrapper:
            if wrapper.conditions:
                query = query.filter(and_(*wrapper.conditions))
        return query.scalar()

    def exists(self, wrapper: QueryWrapper) -> bool:
        """
        判断是否存在

        Args:
            wrapper: 查询条件包装器

        Returns:
            是否存在
        """
        return self.count(wrapper) > 0

    def page(self, page: int, page_size: int, wrapper: Optional[QueryWrapper] = None) -> Dict[str, Any]:
        """
        分页查询

        Args:
            page: 页码（从 1 开始）
            page_size: 每页大小
            wrapper: 查询条件包装器（可选）

        Returns:
            分页结果字典，包含 total, page, page_size, items
        """
        # 查询总数
        total = self.count(wrapper)

        # 查询数据
        query = (
            self.db.query(self.model_class)
            .filter(
                and_(
                    self.model_class.del_flag == 0
                )
            )
        )
        if wrapper:
            query = wrapper.build_query(query)

        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }

    # ==================== 便捷方法 ====================

    def query_wrapper(self) -> QueryWrapper:
        """
        创建查询条件包装器

        Returns:
            QueryWrapper 实例
        """
        return QueryWrapper(self.model_class)

    def save_or_update(self, entity: T) -> T:
        """
        保存或更新（根据 ID 是否存在判断）

        Args:
            entity: 实体对象

        Returns:
            保存或更新后的实体
        """
        if hasattr(entity, 'id') and entity.id and self.get_by_id(entity.id):
            self.update_by_id(entity)
            return entity
        else:
            return self.save(entity)

    def list_all(self) -> List[T]:
        """
        查询所有记录（不包含已删除）

        Returns:
            实体列表
        """
        return self.list()


# """
# BaseRepository 使用示例
#
# 类似 MyBatis-Plus 的 CRUD 操作示例
# """
# from sqlalchemy import Column, String, Integer
#
#
# # ==================== 1. 定义模型 ====================
#
# class User(BaseDBModel):
#     """用户模型"""
#     __tablename__ = "users"
#
#     username = Column(String(50), nullable=False, comment="用户名")
#     email = Column(String(100), comment="邮箱")
#     age = Column(Integer, comment="年龄")
#     status = Column(Integer, default=1, comment="状态：1-正常，0-禁用")
#
#
# # ==================== 2. 定义 Repository ====================
#
# class UserRepository(BaseRepository[User]):
#     """用户 Repository"""
#
#     def __init__(self, db: Session):
#         super().__init__(db, User)
#
#     # 可以添加自定义方法
#     def find_by_username(self, username: str):
#         """根据用户名查询"""
#         wrapper = self.query_wrapper().eq("username", username)
#         return self.get_one(wrapper)
#
#     def find_active_users(self):
#         """查询所有活跃用户"""
#         wrapper = self.query_wrapper().eq("status", 1)
#         return self.list(wrapper)
