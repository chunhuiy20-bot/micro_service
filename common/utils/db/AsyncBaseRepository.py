"""
AsyncBaseRepository - 异步版本的 Repository 基类
配合 AsyncDBManager 使用，提供异步 CRUD 操作
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, desc, asc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import Select
from common.model.BaseDBModel import BaseDBModel

# 定义泛型类型
T = TypeVar('T', bound=BaseDBModel)


class AsyncQueryWrapper:
    """异步查询条件包装器"""

    def __init__(self, model_class: Type[BaseDBModel]):
        self.model_class = model_class
        self.conditions = []
        self.order_by_clauses = []
        self._limit = None
        self._offset = None

    def eq(self, field: str, value: Any) -> "AsyncQueryWrapper":
        """等于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column == value)
        return self

    def ne(self, field: str, value: Any) -> "AsyncQueryWrapper":
        """不等于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column != value)
        return self

    def gt(self, field: str, value: Any) -> "AsyncQueryWrapper":
        """大于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column > value)
        return self

    def ge(self, field: str, value: Any) -> "AsyncQueryWrapper":
        """大于等于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column >= value)
        return self

    def lt(self, field: str, value: Any) -> "AsyncQueryWrapper":
        """小于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column < value)
        return self

    def le(self, field: str, value: Any) -> "AsyncQueryWrapper":
        """小于等于条件"""
        if value is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column <= value)
        return self

    def like(self, field: str, value: str) -> "AsyncQueryWrapper":
        """模糊查询"""
        if value:
            column = getattr(self.model_class, field)
            self.conditions.append(column.like(f"%{value}%"))
        return self

    def like_left(self, field: str, value: str) -> "AsyncQueryWrapper":
        """左模糊查询"""
        if value:
            column = getattr(self.model_class, field)
            self.conditions.append(column.like(f"%{value}"))
        return self

    def like_right(self, field: str, value: str) -> "AsyncQueryWrapper":
        """右模糊查询"""
        if value:
            column = getattr(self.model_class, field)
            self.conditions.append(column.like(f"{value}%"))
        return self

    def in_(self, field: str, values: List[Any]) -> "AsyncQueryWrapper":
        """IN 查询"""
        if values:
            column = getattr(self.model_class, field)
            self.conditions.append(column.in_(values))
        return self

    def not_in(self, field: str, values: List[Any]) -> "AsyncQueryWrapper":
        """NOT IN 查询"""
        if values:
            column = getattr(self.model_class, field)
            self.conditions.append(~column.in_(values))
        return self

    def between(self, field: str, start: Any, end: Any) -> "AsyncQueryWrapper":
        """BETWEEN 查询"""
        if start is not None and end is not None:
            column = getattr(self.model_class, field)
            self.conditions.append(column.between(start, end))
        return self

    def is_null(self, field: str) -> "AsyncQueryWrapper":
        """IS NULL 查询"""
        column = getattr(self.model_class, field)
        self.conditions.append(column.is_(None))
        return self

    def is_not_null(self, field: str) -> "AsyncQueryWrapper":
        """IS NOT NULL 查询"""
        column = getattr(self.model_class, field)
        self.conditions.append(column.isnot(None))
        return self

    def order_by_asc(self, *fields: str) -> "AsyncQueryWrapper":
        """升序排序"""
        for field in fields:
            column = getattr(self.model_class, field)
            self.order_by_clauses.append(asc(column))
        return self

    def order_by_desc(self, *fields: str) -> "AsyncQueryWrapper":
        """降序排序"""
        for field in fields:
            column = getattr(self.model_class, field)
            self.order_by_clauses.append(desc(column))
        return self

    def limit(self, limit: int) -> "AsyncQueryWrapper":
        """限制返回数量"""
        self._limit = limit
        return self

    def offset(self, offset: int) -> "AsyncQueryWrapper":
        """偏移量"""
        self._offset = offset
        return self

    def build_statement(self, stmt: Select) -> Select:
        """构建查询语句"""
        if self.conditions:
            stmt = stmt.where(and_(*self.conditions))
        if self.order_by_clauses:
            stmt = stmt.order_by(*self.order_by_clauses)
        if self._offset is not None:
            stmt = stmt.offset(self._offset)
        if self._limit is not None:
            stmt = stmt.limit(self._limit)
        return stmt


class AsyncBaseRepository(Generic[T]):
    """
    异步通用 Repository 基类

    使用示例:
        class UserRepository(AsyncBaseRepository[User]):
            def __init__(self, db: AsyncSession):
                super().__init__(db, User)

        # 使用
        async with multi_db.session("main") as db:
            user_repo = UserRepository(db)
            user = await user_repo.get_by_id(1)
    """

    def __init__(self, db: AsyncSession, model_class: Type[T]):
        self.db = db
        self.model_class = model_class

    # ==================== 基础 CRUD 操作 ====================

    async def save(self, entity: T) -> T:
        """
        保存实体（新增）

        Args:
            entity: 实体对象

        Returns:
            保存后的实体
        """
        try:
            self.db.add(entity)
            await self.db.flush()
            await self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def save_batch(self, entities: List[T]) -> List[T]:
        """
        批量保存

        Args:
            entities: 实体列表

        Returns:
            保存后的实体列表
        """
        try:
            self.db.add_all(entities)
            await self.db.flush()
            for entity in entities:
                await self.db.refresh(entity)
            return entities
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def update_by_id(self, entity: T) -> bool:
        """
        根据 ID 更新实体

        Args:
            entity: 实体对象（必须包含 id）

        Returns:
            是否更新成功
        """
        try:
            await self.db.merge(entity)
            await self.db.flush()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def update_by_id_selective(self, id: int, updates: Dict[str, Any]) -> bool:
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

            stmt = select(self.model_class).where(
                and_(
                    self.model_class.id == id,
                    self.model_class.del_flag == 0
                )
            )
            result = await self.db.execute(stmt)
            entity = result.scalar_one_or_none()

            if entity:
                for key, value in updates.items():
                    setattr(entity, key, value)
                await self.db.flush()
                return True
            return False
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def remove_by_id(self, id: int, physical: bool = False) -> bool:
        """
        根据 ID 删除（默认逻辑删除）

        Args:
            id: 实体 ID
            physical: 是否物理删除，默认 False（逻辑删除）

        Returns:
            是否删除成功
        """
        try:
            stmt: Select[T] = select(self.model_class).where(
                self.model_class.id == id  # type: ignore[arg-type]
            )
            if not physical:
                stmt = stmt.where(self.model_class.del_flag == 0)  # type: ignore[arg-type]

            result = await self.db.execute(stmt)
            entity = result.scalar_one_or_none()

            if entity:
                if physical:
                    await self.db.delete(entity)
                else:
                    entity.del_flag = 1
                await self.db.flush()
                return True
            return False
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def remove_by_ids(self, ids: List[int], physical: bool = False) -> int:
        """
        根据 ID 列表批量删除

        Args:
            ids: ID 列表
            physical: 是否物理删除

        Returns:
            删除的记录数
        """
        try:
            stmt = select(self.model_class).where(self.model_class.id.in_(ids))
            if not physical:
                stmt = stmt.where(self.model_class.del_flag == 0)  # type: ignore[arg-type]

            result = await self.db.execute(stmt)
            entities = result.scalars().all()

            count = 0
            for entity in entities:
                if physical:
                    await self.db.delete(entity)
                else:
                    entity.del_flag = 1
                count += 1

            await self.db.flush()
            return count
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def get_by_id(self, id: int) -> Optional[T]:
        """
        根据 ID 查询

        Args:
            id: 实体 ID

        Returns:
            实体对象或 None
        """
        stmt = select(self.model_class).where(
            and_(
                self.model_class.id == id,
                self.model_class.del_flag == 0
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_one(self, wrapper: AsyncQueryWrapper) -> Optional[T]:
        """
        根据条件查询单个实体

        Args:
            wrapper: 查询条件包装器

        Returns:
            实体对象或 None
        """
        stmt = select(self.model_class).where(self.model_class.del_flag == 0)  # type: ignore[arg-type]
        stmt = wrapper.build_statement(stmt)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, wrapper: Optional[AsyncQueryWrapper] = None) -> List[T]:
        """
        查询列表

        Args:
            wrapper: 查询条件包装器（可选）

        Returns:
            实体列表
        """
        stmt = select(self.model_class).where(self.model_class.del_flag == 0)  # type: ignore[arg-type]
        if wrapper:
            stmt = wrapper.build_statement(stmt)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_ids(self, ids: List[int]) -> List[T]:
        """
        根据 ID 列表查询

        Args:
            ids: ID 列表

        Returns:
            实体列表
        """
        stmt = select(self.model_class).where(
            and_(
                self.model_class.id.in_(ids),
                self.model_class.del_flag == 0
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self, wrapper: Optional[AsyncQueryWrapper] = None) -> int:
        """
        统计数量

        Args:
            wrapper: 查询条件包装器（可选）

        Returns:
            记录数
        """
        stmt = select(func.count(self.model_class.id)).where(
            self.model_class.del_flag == 0  # type: ignore[arg-type]
        )
        if wrapper and wrapper.conditions:
            stmt = stmt.where(and_(*wrapper.conditions))
        result = await self.db.execute(stmt)
        return result.scalar()

    async def exists(self, wrapper: AsyncQueryWrapper) -> bool:
        """
        判断是否存在

        Args:
            wrapper: 查询条件包装器

        Returns:
            是否存在
        """
        return await self.count(wrapper) > 0

    async def page(self, page: int, page_size: int, wrapper: Optional[AsyncQueryWrapper] = None) -> Dict[str, Any]:
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
        total = await self.count(wrapper)

        # 查询数据
        stmt = select(self.model_class).where(self.model_class.del_flag == 0)  # type: ignore[arg-type]
        if wrapper:
            stmt = wrapper.build_statement(stmt)

        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }

    # ==================== 便捷方法 ====================

    def query_wrapper(self) -> AsyncQueryWrapper:
        """
        创建查询条件包装器

        Returns:
            AsyncQueryWrapper 实例
        """
        return AsyncQueryWrapper(self.model_class)

    async def save_or_update(self, entity: T) -> T:
        """
        保存或更新（根据 ID 是否存在判断）

        Args:
            entity: 实体对象

        Returns:
            保存或更新后的实体
        """
        if hasattr(entity, 'id') and entity.id and await self.get_by_id(entity.id):
            await self.update_by_id(entity)
            return entity
        else:
            return await self.save(entity)

    async def list_all(self) -> List[T]:
        """
        查询所有记录（不包含已删除）

        Returns:
            实体列表
        """
        return await self.list()
