import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from common.utils.db.AsyncBaseRepository import AsyncBaseRepository
from account_service.model.User import User
from common.utils.db.MultiAsyncDBManager import multi_db
from common.utils.env.EnvLoader import load_service_env
# 加载环境变量
load_service_env(__file__)


class UserRepository(AsyncBaseRepository[User]):
    """用户数据访问层"""

    def __init__(self, db: Optional[AsyncSession] = None, db_name: Optional[str] = None):
        db_url = os.getenv("MYSQL_CONFIG_ASYNC")
        multi_db.add_database("main", db_url)
        super().__init__(db, User, db_name)


# 初始化数据库连接
user_repo = UserRepository(db_name="main")


# async def example_no_transaction():
#     # 1. 添加数据库配置（只需要配置一次）
#     db_url = os.getenv("MYSQL_CONFIG_ASYNC")
#
#     # 如果环境变量未设置，使用默认值（仅用于测试）
#     if not db_url:
#         db_url = "mysql+aiomysql://root:123@127.0.0.1:3306/test?charset=utf8mb4"
#         print(f"警告：使用默认数据库连接: {db_url}")
#     else:
#         print(f"数据库连接字符串: {db_url}")
#
#     multi_db.add_database("main", db_url)
#
#
#     # 2. 直接使用，完全不需要 async with！
#     user_repo = UserRepository(db_name="main")
#
#     # # 查询用户
#     # user = await user_repo.get_by_id(1)
#     # print(f"User 查询结果: {user}")
#     # #
#     # # # 条件查询
#     # # wrapper = user_repo.query_wrapper().eq("name", "admin")
#     # # user = await user_repo.get_one(wrapper)
#     # #
#     # 列表查询
#     users = await user_repo.list()
#     print(f"Total users: {len(users)}")
#     for user in users:
#         user: User = user
#         print(f"User: {user.id}")
#     #
#     # # 分页查询
#     # page_result = await user_repo.page(page=1, page_size=10)
#     # print(f"Page result: {page_result}")
#     #
#     # # 保存用户
#     # new_user = User(name="test_user")
#     # saved_user = await user_repo.save(new_user)
#     # print(f"Saved user: {saved_user}")
#     #
#     # # 更新用户
#     # await user_repo.update_by_id_selective(saved_user.id, {"name": "updated_name"})
#     # print("User updated")
#
#
# async def example_with_transaction():
#     """使用事务的示例 - 多个操作在同一个事务中，要么全部成功，要么全部回滚"""
#     # 1. 添加数据库配置
#     multi_db.add_database("main", os.getenv("MYSQL_CONFIG_ASYNC"))
#     user_repo = UserRepository(db_name="main")
#     # 2. 使用 async with 开启事务
#     try:
#         async with user_repo:
#             # 创建新用户
#             new_user = User(name="transaction_test")
#             saved_user = await user_repo.save(new_user)
#             print(f"创建用户: {saved_user.id}")
#
#             # 更新用户信息
#             await user_repo.update_by_id_selective(
#                 saved_user.id,
#                 {"name": "updated_name"}
#             )
#             print(f"更新用户: {saved_user.id}")
#
#             # 查询验证
#             updated_user = await user_repo.get_by_id(saved_user.id)
#             print(f"验证更新: {updated_user.name}")
#
#             # 如果这里抛出异常，上面的所有操作都会回滚
#             # a = 1/0
#
#             # 所有操作成功，事务自动提交
#             print("事务提交成功！")
#
#     except Exception as e:
#         print(f"事务失败，已回滚: {e}")
#
#
# async def example_compare():
#     """对比：不使用事务 vs 使用事务"""
#     multi_db.add_database("main", os.getenv("MYSQL_CONFIG_ASYNC"))
#
#     print("=== 场景1：不使用事务（每个操作独立提交）===")
#     user_repo = UserRepository(db_name="main")
#
#     try:
#         # 操作1：创建用户（独立事务，会立即提交）
#         user1 = User(name="user1")
#         saved_user1 = await user_repo.save(user1)
#         print(f"✓ 用户1已保存: {saved_user1.id}")
#
#         # 操作2：创建另一个用户（独立事务，会立即提交）
#         user2 = User(name="user2")
#         saved_user2 = await user_repo.save(user2)
#         print(f"✓ 用户2已保存: {saved_user2.id}")
#
#         # 模拟错误
#         raise Exception("发生错误！")
#
#         # 即使这里出错，上面的两个用户已经保存到数据库了
#     except Exception as e:
#         print(f"✗ 错误: {e}")
#         print("注意：虽然出错了，但 user1 和 user2 已经保存到数据库")
#
#     print("\n=== 场景2：使用事务（所有操作在同一个事务中）===")
#     try:
#         async with UserRepository(db_name="main") as repo:
#             # 操作1：创建用户（未提交）
#             user3 = User(name="user3")
#             saved_user3 = await repo.save(user3)
#             print(f"✓ 用户3已保存: {saved_user3.id}")
#
#             # 操作2：创建另一个用户（未提交）
#             user4 = User(name="user4")
#             saved_user4 = await repo.save(user4)
#             print(f"✓ 用户4已保存: {saved_user4.id}")
#
#             # 模拟错误
#             raise Exception("发生错误！")
#
#             # 如果没有错误，退出 async with 时会自动提交
#     except Exception as e:
#         print(f"✗ 错误: {e}")
#         print("注意：因为使用了事务，user3 和 user4 都被回滚了，数据库中不存在")
#
#

# if __name__ == "__main__":
#     import asyncio
#     # 运行无事务测试
#     # asyncio.run(example_no_transaction())
#
#     # 运行事务测试
#     asyncio.run(example_with_transaction())
#
#     # 运行对比测试
#     # asyncio.run(example_compare())

