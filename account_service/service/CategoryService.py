from typing import Optional, List
from account_service.repository.CategoryRepository import CategoryRepository
from account_service.model.Category import Category
from account_service.schemas.request.CategoryRequestSchemas import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    SystemCategoryCreateRequest,
    SystemCategoryUpdateRequest,
)
from account_service.schemas.response.CategoryResponseSchemas import CategoryResponse
from common.schemas.CommonResult import Result
from common.utils.decorators.AsyncDecorators import async_retry
from common.utils.decorators.WithRepoDecorators import with_repo


class CategoryService:

    # ==================== 系统分类管理 ====================

    @async_retry(max_retries=3, delay=3)
    @with_repo(CategoryRepository, db_name="main")
    async def create_system_category(self, category_repo: CategoryRepository, request: SystemCategoryCreateRequest) -> Result[CategoryResponse]:
        """
        方法说明: 新增系统默认分类
        作者: yangchunhui
        创建时间: 2026/2/25
        修改历史:
        2026/2/25 - yangchunhui - 初始版本
        """
        # 检查同类型下系统分类名称是否重复
        wrapper = category_repo.query_wrapper().eq("name", request.name).eq("category_type", request.category_type).eq("is_system", True)
        if await category_repo.get_one(wrapper):
            return Result.fail(f"系统分类 '{request.name}' 已存在")

        new_category = Category(
            name=request.name,
            category_type=request.category_type,
            user_id=None,
            is_system=True,
            icon=request.icon,
            sort_order=request.sort_order,
        )
        try:
            saved = await category_repo.save(new_category)
            return Result.success(CategoryResponse.model_validate(saved))
        except Exception as e:
            return Result.fail(f"新增系统分类失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(CategoryRepository, db_name="main")
    async def update_system_category(self, category_repo: CategoryRepository, category_id: int, request: SystemCategoryUpdateRequest) -> Result[bool]:
        """
        方法说明: 修改系统默认分类
        作者: yangchunhui
        创建时间: 2026/2/25
        修改历史:
        2026/2/25 - yangchunhui - 初始版本
        """
        category = await category_repo.get_by_id(category_id)
        if not category:
            return Result.fail("系统分类不存在")
        if not category.is_system:
            return Result.fail("该分类不是系统分类，无法通过此接口修改")

        updates = request.model_dump(exclude_none=True)
        if not updates:
            return Result.fail("没有需要更新的字段")

        try:
            await category_repo.update_by_id_selective(category_id, updates)
            return Result.success(True)
        except Exception as e:
            return Result.fail(f"修改系统分类失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(CategoryRepository, db_name="main")
    async def delete_system_category(self, category_repo: CategoryRepository, category_id: int) -> Result[bool]:
        """
        方法说明: 删除系统默认分类
        作者: yangchunhui
        创建时间: 2026/2/25
        修改历史:
        2026/2/25 - yangchunhui - 初始版本
        """
        category = await category_repo.get_by_id(category_id)
        if not category:
            return Result.fail("系统分类不存在")
        if not category.is_system:
            return Result.fail("该分类不是系统分类，无法通过此接口删除")

        try:
            await category_repo.remove_by_id(category_id)
            return Result.success(True)
        except Exception as e:
            return Result.fail(f"删除系统分类失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(CategoryRepository, db_name="main")
    async def list_system_categories(self, category_repo: CategoryRepository) -> Result[List[CategoryResponse]]:
        """
        方法说明: 查询所有系统默认分类
        作者: yangchunhui
        创建时间: 2026/2/25
        修改历史:
        2026/2/25 - yangchunhui - 初始版本
        """
        wrapper = category_repo.query_wrapper().eq("is_system", True).order_by_asc("sort_order")
        categories = await category_repo.list(wrapper)
        return Result.success([CategoryResponse.model_validate(c) for c in categories])

    # ==================== 用户分类管理 ====================

    @async_retry(max_retries=3, delay=3)
    @with_repo(CategoryRepository, db_name="main")
    async def create_user_category(self, category_repo: CategoryRepository, user_id: int, request: CategoryCreateRequest) -> Result[CategoryResponse]:
        """
        方法说明: 用户新增自定义分类
        作者: yangchunhui
        创建时间: 2026/2/25
        修改历史:
        2026/2/25 - yangchunhui - 初始版本
        """
        # 检查用户自定义分类数量是否超限
        count_wrapper = category_repo.query_wrapper().eq("user_id", user_id).eq("is_system", False)
        if await category_repo.count(count_wrapper) >= 100:
            return Result.fail("自定义分类数量已达上限（100个）")

        # 检查该用户下同类型分类名称是否重复
        wrapper = category_repo.query_wrapper().eq("name", request.name).eq("category_type", request.category_type).eq("user_id", user_id)
        if await category_repo.get_one(wrapper):
            return Result.fail(f"分类 '{request.name}' 已存在")

        new_category = Category(
            name=request.name,
            category_type=request.category_type,
            user_id=user_id,
            is_system=False,
            icon=request.icon,
            sort_order=request.sort_order,
        )
        try:
            saved = await category_repo.save(new_category)
            return Result.success(CategoryResponse.model_validate(saved))
        except Exception as e:
            return Result.fail(f"新增分类失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(CategoryRepository, db_name="main")
    async def update_user_category(self, category_repo: CategoryRepository, user_id: int, category_id: int, request: CategoryUpdateRequest) -> Result[bool]:
        """
        方法说明: 用户修改自定义分类
        作者: yangchunhui
        创建时间: 2026/2/25
        修改历史:
        2026/2/25 - yangchunhui - 初始版本
        """
        category = await category_repo.get_by_id(category_id)
        if not category:
            return Result.fail("分类不存在")
        if category.is_system:
            return Result.fail("系统分类不允许修改")
        if category.user_id != user_id:
            return Result.fail("无权限修改该分类")

        updates = request.model_dump(exclude_none=True)
        if not updates:
            return Result.fail("没有需要更新的字段")

        try:
            await category_repo.update_by_id_selective(category_id, updates)
            return Result.success(True)
        except Exception as e:
            return Result.fail(f"修改分类失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(CategoryRepository, db_name="main")
    async def delete_user_category(self, category_repo: CategoryRepository, user_id: int, category_id: int) -> Result[bool]:
        """
        方法说明: 用户删除自定义分类
        作者: yangchunhui
        创建时间: 2026/2/25
        修改历史:
        2026/2/25 - yangchunhui - 初始版本
        """
        category = await category_repo.get_by_id(category_id)
        if not category:
            return Result.fail("分类不存在")
        if category.is_system:
            return Result.fail("系统分类不允许删除")
        if category.user_id != user_id:
            return Result.fail("无权限删除该分类")

        try:
            await category_repo.remove_by_id(category_id)
            return Result.success(True)
        except Exception as e:
            return Result.fail(f"删除分类失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(CategoryRepository, db_name="main")
    async def list_categories(self, category_repo: CategoryRepository, user_id: Optional[int] = None, category_type: Optional[int] = None) -> Result[List[CategoryResponse]]:
        """
        方法说明: 查询分类列表。无 user_id 只返回系统分类；有 user_id 返回系统分类 + 该用户自定义分类；category_type 可过滤收支类型
        作者: yangchunhui
        创建时间: 2026/2/25
        修改历史:
        2026/2/25 - yangchunhui - 初始版本
        """
        system_wrapper = category_repo.query_wrapper().eq("is_system", True).eq("category_type", category_type).order_by_asc("sort_order")
        system_categories = await category_repo.list(system_wrapper)

        if user_id is None:
            return Result.success([CategoryResponse.model_validate(c) for c in system_categories])

        user_wrapper = category_repo.query_wrapper().eq("user_id", user_id).eq("is_system", False).eq("category_type", category_type).order_by_asc("sort_order")
        user_categories = await category_repo.list(user_wrapper)

        all_categories = system_categories + user_categories
        return Result.success([CategoryResponse.model_validate(c) for c in all_categories])


category_service = CategoryService()
