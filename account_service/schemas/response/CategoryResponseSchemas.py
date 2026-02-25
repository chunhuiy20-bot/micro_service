from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime


class CategoryResponse(BaseModel):
    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    category_type: int = Field(..., description="类型: 1-支出, 2-收入")
    user_id: Optional[int] = Field(None, description="用户ID，为空表示系统分类")
    is_system: bool = Field(..., description="是否系统预设分类")
    icon: Optional[str] = Field(None, description="图标标识")
    sort_order: int = Field(0, description="排序顺序")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    @field_serializer('id')
    def serialize_id(self, value: int) -> str:
        return str(value)

    @field_serializer('user_id')
    def serialize_user_id(self, value: Optional[int]) -> Optional[str]:
        return str(value) if value is not None else None

    class Config:
        from_attributes = True
