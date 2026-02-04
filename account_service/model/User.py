from sqlalchemy import String, Column

from common.model.BaseDBModel import BaseDBModel


class User(BaseDBModel):
    __tablename__ = "user"
    name = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)