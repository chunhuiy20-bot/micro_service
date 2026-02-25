"""
文件名: RoleDepends.py
作者: yangchunhui
创建日期: 2026/2/25
联系方式: chunhuiy20@gmail.com
版本号: 1.0
更改时间: 2026/2/25
描述: FastAPI 角色权限依赖工厂，生成可直接用于路由 Depends 的角色校验函数。
      从 request.state.user_extra 中取 role 字段判断，依赖 AuthMiddleware 提前注入。

修改历史:
2026/2/25 - yangchunhui - 初始版本

依赖:
- fastapi: Web 框架
- AuthMiddleware: 需提前注入 request.state.user_extra

使用示例:
    @router.post("/system", dependencies=[Depends(require_role("admin"))])
    @router.post("/user", dependencies=[Depends(require_role("admin", "level_1"))])
"""

from fastapi import Request, HTTPException


def require_role(*roles: str):
    """
    角色权限依赖工厂，从 request.state.user_extra 中取 role 判断

    用法:
        @router.post("/system", dependencies=[Depends(require_role("admin"))])
        @router.post("/user", dependencies=[Depends(require_role("admin", "level_1"))])
    """
    async def _check(request: Request):
        extra = getattr(request.state, "user_extra", None) or {}
        role = extra.get("role")
        if role not in roles:
            raise HTTPException(status_code=403, detail="权限不足")

    return _check
