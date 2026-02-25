from typing import Optional
from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., description="分类名称")
    category_type: int = Field(..., description="类型: 1-支出, 2-收入")
    icon: Optional[str] = Field(None, description="图标标识")
    sort_order: int = Field(0, description="排序顺序")


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="分类名称")
    category_type: Optional[int] = Field(None, description="类型: 1-支出, 2-收入")
    icon: Optional[str] = Field(None, description="图标标识")
    sort_order: Optional[int] = Field(None, description="排序顺序")


class SystemCategoryCreateRequest(BaseModel):
    name: str = Field(..., description="分类名称")
    category_type: int = Field(..., description="类型: 1-支出, 2-收入")
    icon: Optional[str] = Field(None, description="图标标识")
    sort_order: int = Field(0, description="排序顺序")


class SystemCategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="分类名称")
    category_type: Optional[int] = Field(None, description="类型: 1-支出, 2-收入")
    icon: Optional[str] = Field(None, description="图标标识")
    sort_order: Optional[int] = Field(None, description="排序顺序")
