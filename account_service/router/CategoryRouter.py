"""
文件名: CategoryRouter.py
作者: yangchunhui
创建日期: 2026/2/25
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/25
描述: 分类服务路由，提供系统分类管理和用户自定义分类管理接口

修改历史:
2026/2/25 - yangchunhui - 初始版本

依赖:
TODO: 列出主要依赖

使用示例:
TODO: 添加使用示例
"""

from typing import Optional
from fastapi import Query, Request, HTTPException, Depends
from account_service.schemas.request.CategoryRequestSchemas import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    SystemCategoryCreateRequest,
    SystemCategoryUpdateRequest,
)
from account_service.service.CategoryService import category_service
from common.utils.jwt.RoleDepends import require_role
from common.utils.router.CustomRouter import CustomAPIRouter

router = CustomAPIRouter(
    prefix="/api/account/category",
    tags=["记账软件分类服务相关API"],
    auto_log=True,
    logger_name="account-service--2",
)


# ==================== 查询接口 ====================

"""
接口说明: 查询分类列表。无 user_id 只返回系统默认分类；有 user_id 返回系统分类 + 用户自定义分类
作者: yangchunhui
创建时间: 2026/2/25
修改历史: 2026/2/25 - yangchunhui - 初始版本
"""
@router.get("/list", summary="查询分类列表", dependencies=[Depends(require_role("admin"))])
async def list_categories(
    user_id: Optional[int] = Query(None, description="用户ID，不传则只返回系统默认分类"),
    category_type: Optional[int] = Query(None, description="分类类型: 1-支出, 2-收入，不传则不区分"),
):
    return await category_service.list_categories(user_id=user_id, category_type=category_type)


# ==================== 系统分类管理 ====================

"""
接口说明: 新增系统默认分类
作者: yangchunhui
创建时间: 2026/2/25
修改历史: 2026/2/25 - yangchunhui - 初始版本
"""
@router.post("/system", summary="新增系统默认分类")
async def create_system_category(request: SystemCategoryCreateRequest):
    return await category_service.create_system_category(request)


"""
接口说明: 修改系统默认分类
作者: yangchunhui
创建时间: 2026/2/25
修改历史: 2026/2/25 - yangchunhui - 初始版本
"""
@router.post("/system/{category_id}/update", summary="修改系统默认分类")
async def update_system_category(category_id: int, request: SystemCategoryUpdateRequest):
    return await category_service.update_system_category(category_id, request)


"""
接口说明: 删除系统默认分类
作者: yangchunhui
创建时间: 2026/2/25
修改历史: 2026/2/25 - yangchunhui - 初始版本
"""
@router.post("/system/{category_id}/delete", summary="删除系统默认分类")
async def delete_system_category(category_id: int):
    return await category_service.delete_system_category(category_id)


"""
接口说明: 查询所有系统默认分类
作者: yangchunhui
创建时间: 2026/2/25
修改历史: 2026/2/25 - yangchunhui - 初始版本
"""
@router.get("/system/list", summary="查询所有系统默认分类")
async def list_system_categories():
    return await category_service.list_system_categories()


# ==================== 用户自定义分类管理 ====================

"""
接口说明: 用户新增自定义分类
作者: yangchunhui
创建时间: 2026/2/25
修改历史: 2026/2/25 - yangchunhui - 初始版本
"""
@router.post("/user/{user_id}", summary="用户新增自定义分类", dependencies=[Depends(require_role("admin"))])
async def create_user_category(user_id: int, request: CategoryCreateRequest, http_request: Request):
    jwt_user_id = http_request.state.user_id
    if str(user_id) != str(jwt_user_id):
        raise HTTPException(status_code=403, detail="无权限操作其他用户的分类")
    return await category_service.create_user_category(user_id, request)


"""
接口说明: 用户修改自定义分类
作者: yangchunhui
创建时间: 2026/2/25
修改历史: 2026/2/25 - yangchunhui - 初始版本
"""
@router.post("/user/{user_id}/{category_id}/update", summary="用户修改自定义分类", dependencies=[Depends(require_role("admin"))])
async def update_user_category(user_id: int, category_id: int, request: CategoryUpdateRequest):
    return await category_service.update_user_category(user_id, category_id, request)


"""
接口说明: 用户删除自定义分类
作者: yangchunhui
创建时间: 2026/2/25
修改历史: 2026/2/25 - yangchunhui - 初始版本
"""
@router.post("/user/{user_id}/{category_id}/delete", summary="用户删除自定义分类")
async def delete_user_category(user_id: int, category_id: int):
    return await category_service.delete_user_category(user_id, category_id)
