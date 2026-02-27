from fastapi import Request, HTTPException
from common.utils.router.CustomRouter import CustomAPIRouter
from stock_service.schemas.request.UserStockRequestSchemas import UserStockAddRequest, UserStockUpdateRequest
from stock_service.service.UserStockService import user_stock_service

router = CustomAPIRouter(
    prefix="/api/stock/user",
    tags=["用户自选股票"],
    auto_log=True,
    logger_name="stock-service",
)


"""
接口说明: 查询用户自选列表
"""
@router.get("/{user_id}/list", summary="查询用户自选列表")
async def list_by_user(user_id: int, request: Request):
    # jwt_user_id = request.state.user_id
    # if str(user_id) != str(jwt_user_id):
    #     raise HTTPException(status_code=403, detail="无权限查看其他用户的自选")
    return await user_stock_service.list_by_user(user_id=user_id)


"""
接口说明: 添加自选股票
"""
@router.post("/{user_id}/add", summary="添加自选股票")
async def add(user_id: int, body: UserStockAddRequest, request: Request):
    # jwt_user_id = request.state.user_id
    # if str(user_id) != str(jwt_user_id):
    #     raise HTTPException(status_code=403, detail="无权限操作其他用户的自选")
    return await user_stock_service.add(user_id=user_id, request=body)


"""
接口说明: 修改自选股票信息
"""
@router.post("/{user_id}/{stock_id}/update", summary="修改自选股票信息")
async def update(user_id: int, stock_id: int, body: UserStockUpdateRequest, request: Request):
    # jwt_user_id = request.state.user_id
    # if str(user_id) != str(jwt_user_id):
    #     raise HTTPException(status_code=403, detail="无权限操作其他用户的自选")
    return await user_stock_service.update(user_id=user_id, stock_id=stock_id, request=body)


"""
接口说明: 删除自选股票
"""
@router.post("/{user_id}/{stock_id}/delete", summary="删除自选股票")
async def remove(user_id: int, stock_id: int, request: Request):
    # jwt_user_id = request.state.user_id
    # if str(user_id) != str(jwt_user_id):
    #     raise HTTPException(status_code=403, detail="无权限操作其他用户的自选")
    return await user_stock_service.remove(user_id=user_id, stock_id=stock_id)
