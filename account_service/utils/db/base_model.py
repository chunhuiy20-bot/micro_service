"""
SQLAlchemy 通用基类封装
提供类似 MyBatis-Plus 的 CRUD 功能
"""
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any, Tuple
from sqlalchemy import create_engine, Column, Integer, DateTime, func, select, update, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as SQLSession
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# 泛型类型
T = TypeVar('T', bound=Base)


class BaseDBModel(Base):
    """数据库模型基类，提供通用字段"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PageResult(BaseModel):
    """分页结果"""
    total: int
    page: int
    page_size: int
    pages: int
    records: List[Dict[str, Any]]


class BaseRepository(Generic[T]):
    """
    通用 Repository 基类
    提供类似 MyBatis-Plus 的 CRUD 操作
    """
    
    def __init__(self, model: Type[T], session: SQLSession):
        """
        初始化 Repository
        
        Args:
            model: SQLAlchemy 模型类
            session: 数据库会话
        """
        self.model = model
        self.session = session
    
    # ==================== 查询操作 ====================
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        根据 ID 查询单条记录
        
        Args:
            id: 主键ID
            
        Returns:
            模型实例或 None
        """
        return self.session.get(self.model, id)
    
    def get_one(self, **kwargs) -> Optional[T]:
        """
        根据条件查询单条记录
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            模型实例或 None
        """
        stmt = select(self.model).filter_by(**kwargs)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def list_all(self) -> List[T]:
        """
        查询所有记录
        
        Returns:
            模型实例列表
        """
        stmt = select(self.model)
        return list(self.session.execute(stmt).scalars().all())
    
    def list_by_ids(self, ids: List[int]) -> List[T]:
        """
        根据 ID 列表批量查询
        
        Args:
            ids: ID 列表
            
        Returns:
            模型实例列表
        """
        stmt = select(self.model).where(self.model.id.in_(ids))
        return list(self.session.execute(stmt).scalars().all())
    
    def list_by_condition(self, **kwargs) -> List[T]:
        """
        根据条件查询列表
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            模型实例列表
        """
        stmt = select(self.model).filter_by(**kwargs)
        return list(self.session.execute(stmt).scalars().all())
    
    def page(
        self,
        page: int = 1,
        page_size: int = 10,
        order_by: Optional[str] = None,
        **kwargs
    ) -> PageResult:
        """
        分页查询
        
        Args:
            page: 页码（从1开始）
            page_size: 每页大小
            order_by: 排序字段（如 "-id" 表示倒序）
            **kwargs: 查询条件
            
        Returns:
            分页结果
        """
        # 构建查询
        stmt = select(self.model).filter_by(**kwargs)
        
        # 排序
        if order_by:
            if order_by.startswith('-'):
                field = order_by[1:]
                stmt = stmt.order_by(getattr(self.model, field).desc())
            else:
                stmt = stmt.order_by(getattr(self.model, order_by))
        
        # 总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.execute(count_stmt).scalar()
        
        # 分页
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        records = self.session.execute(stmt).scalars().all()
        
        return PageResult(
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
            records=[r.to_dict() for r in records]
        )
    
    def count(self, **kwargs) -> int:
        """
        统计记录数
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            记录数
        """
        stmt = select(func.count()).select_from(self.model).filter_by(**kwargs)
        return self.session.execute(stmt).scalar()
    
    def exists(self, **kwargs) -> bool:
        """
        判断记录是否存在
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            是否存在
        """
        return self.count(**kwargs) > 0
    
    # ==================== 插入操作 ====================
    
    def insert(self, entity: T) -> T:
        """
        插入单条记录
        
        Args:
            entity: 模型实例
            
        Returns:
            插入后的模型实例（包含ID）
        """
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def insert_batch(self, entities: List[T]) -> List[T]:
        """
        批量插入
        
        Args:
            entities: 模型实例列表
            
        Returns:
            插入后的模型实例列表
        """
        self.session.add_all(entities)
        self.session.flush()
        return entities
    
    def save(self, **kwargs) -> T:
        """
        保存记录（便捷方法）
        
        Args:
            **kwargs: 字段值
            
        Returns:
            保存后的模型实例
        """
        entity = self.model(**kwargs)
        return self.insert(entity)
    
    # ==================== 更新操作 ====================
    
    def update_by_id(self, id: int, **kwargs) -> bool:
        """
        根据 ID 更新记录
        
        Args:
            id: 主键ID
            **kwargs: 要更新的字段
            
        Returns:
            是否更新成功
        """
        stmt = update(self.model).where(self.model.id == id).values(**kwargs)
        result = self.session.execute(stmt)
        return result.rowcount > 0
    
    def update_by_condition(self, condition: Dict[str, Any], **kwargs) -> int:
        """
        根据条件批量更新
        
        Args:
            condition: 查询条件
            **kwargs: 要更新的字段
            
        Returns:
            更新的记录数
        """
        stmt = update(self.model).filter_by(**condition).values(**kwargs)
        result = self.session.execute(stmt)
        return result.rowcount
    
    def update_entity(self, entity: T) -> T:
        """
        更新实体对象
        
        Args:
            entity: 模型实例
            
        Returns:
            更新后的模型实例
        """
        self.session.merge(entity)
        self.session.flush()
        return entity
    
    # ==================== 删除操作 ====================
    
    def delete_by_id(self, id: int) -> bool:
        """
        根据 ID 删除记录
        
        Args:
            id: 主键ID
            
        Returns:
            是否删除成功
        """
        stmt = delete(self.model).where(self.model.id == id)
        result = self.session.execute(stmt)
        return result.rowcount > 0
    
    def delete_by_ids(self, ids: List[int]) -> int:
        """
        根据 ID 列表批量删除
        
        Args:
            ids: ID 列表
            
        Returns:
            删除的记录数
        """
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = self.session.execute(stmt)
        return result.rowcount
    
    def delete_by_condition(self, **kwargs) -> int:
        """
        根据条件删除
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            删除的记录数
        """
        stmt = delete(self.model).filter_by(**kwargs)
        result = self.session.execute(stmt)
        return result.rowcount
    
    # ==================== 事务操作 ====================
    
    def commit(self):
        """提交事务"""
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"事务提交失败: {e}", exc_info=True)
            raise
    
    def rollback(self):
        """回滚事务"""
        self.session.rollback()
    
    def flush(self):
        """刷新会话"""
        self.session.flush()


# #========================================    使用示例
# """
# 用户模型示例
# """
# from sqlalchemy import Column, String, Integer, Boolean
# from gateway.db.base_model import BaseDBModel, BaseRepository
# from sqlalchemy.orm import Session


# class User(BaseDBModel):
#     """用户模型"""
#     __tablename__ = "users"
    
#     username = Column(String(50), unique=True, nullable=False, comment="用户名")
#     email = Column(String(100), unique=True, nullable=False, comment="邮箱")
#     password = Column(String(255), nullable=False, comment="密码")
#     is_active = Column(Boolean, default=True, comment="是否激活")
#     age = Column(Integer, comment="年龄")


# class UserRepository(BaseRepository[User]):
#     """用户 Repository"""
    
#     def __init__(self, session: Session):
#         super().__init__(User, session)
    
#     # 可以添加自定义方法
#     def get_by_username(self, username: str) -> User:
#         """根据用户名查询"""
#         return self.get_one(username=username)
    
#     def get_active_users(self) -> list[User]:
#         """获取所有激活用户"""
#         return self.list_by_condition(is_active=True)
    
#     def search_by_username(self, keyword: str) -> list[User]:
#         """模糊搜索用户名"""
#         from sqlalchemy import select
#         stmt = select(User).where(User.username.like(f"%{keyword}%"))
#         return list(self.session.execute(stmt).scalars().all())



# """
# FastAPI 应用集成示例
# """
# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from gateway.db.database import init_database, get_db
# from gateway.db.base_model import Base
# from gateway.models.user import User, UserRepository

# app = FastAPI()

# # 初始化数据库
# db_manager = init_database(
#     "mysql+pymysql://root:password@localhost:3306/mydb",
#     echo=True
# )
# db_manager.create_tables(Base)


# # Pydantic 模型
# class UserCreate(BaseModel):
#     username: str
#     email: str
#     password: str
#     age: int = None


# class UserResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     is_active: bool
    
#     class Config:
#         from_attributes = True


# # API 端点
# @app.post("/users", response_model=UserResponse)
# def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
#     """创建用户"""
#     repo = UserRepository(db)
    
#     # 检查用户名是否存在
#     if repo.exists(username=user_data.username):
#         raise HTTPException(status_code=400, detail="用户名已存在")
    
#     # 创建用户
#     user = repo.save(**user_data.dict())
#     repo.commit()
    
#     return user


# @app.get("/users/{user_id}", response_model=UserResponse)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     """获取用户"""
#     repo = UserRepository(db)
#     user = repo.get_by_id(user_id)
    
#     if not user:
#         raise HTTPException(status_code=404, detail="用户不存在")
    
#     return user


# @app.get("/users")
# def list_users(
#     page: int = 1,
#     page_size: int = 10,
#     db: Session = Depends(get_db)
# ):
#     """分页查询用户"""
#     repo = UserRepository(db)
#     return repo.page(page=page, page_size=page_size, order_by="-id")


# @app.put("/users/{user_id}")
# def update_user(
#     user_id: int,
#     username: str = None,
#     email: str = None,
#     db: Session = Depends(get_db)
# ):
#     """更新用户"""
#     repo = UserRepository(db)
    
#     update_data = {}
#     if username:
#         update_data['username'] = username
#     if email:
#         update_data['email'] = email
    
#     success = repo.update_by_id(user_id, **update_data)
#     repo.commit()
    
#     if not success:
#         raise HTTPException(status_code=404, detail="用户不存在")
    
#     return {"message": "更新成功"}


# @app.delete("/users/{user_id}")
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     """删除用户"""
#     repo = UserRepository(db)
#     success = repo.delete_by_id(user_id)
#     repo.commit()
    
#     if not success:
#         raise HTTPException(status_code=404, detail="用户不存在")
    
#     return {"message": "删除成功"}


# @app.post("/users/batch")
# def batch_create_users(users: list[UserCreate], db: Session = Depends(get_db)):
#     """批量创建用户"""
#     repo = UserRepository(db)
    
#     user_entities = [User(**user.dict()) for user in users]
#     repo.insert_batch(user_entities)
#     repo.commit()
    
#     return {"message": f"成功创建 {len(user_entities)} 个用户"}