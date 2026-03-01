from datetime import date
from fastapi import Query
from common.utils.router.CustomRouter import CustomAPIRouter
from stock_service.schemas.structured_ai_response.HighMomentumSectors import HighMomentumSector
from stock_service.service.HotSectorService import hot_sector_service

router = CustomAPIRouter(
    prefix="/api/stock/hot-sector",
    tags=["热门板块"],
    auto_log=True,
    logger_name="stock-service",
)


"""
接口说明: 保存 AI 返回的热门板块数据（存在则覆盖更新）
"""
@router.post("/save", summary="保存热门板块数据")
async def save(body: HighMomentumSector, record_date: date = Query(..., description="采集日期，格式: 2024-01-01")):
    return await hot_sector_service.save(data=body, record_date=record_date)


"""
接口说明: 查询今日热门板块基础信息列表
"""
@router.get("/today/list", summary="查询今日热门板块列表")
async def list_today_brief():
    return await hot_sector_service.list_today_brief()


"""
接口说明: 查询今日某个热门板块详细信息（含产业链及个股）
"""
@router.get("/today/detail", summary="查询今日板块详细信息")
async def get_today_detail(sector_name: str = Query(..., description="板块名称，如 AI半导体")):
    return await hot_sector_service.get_today_detail(sector_name=sector_name)


"""
接口说明: 根据板块 ID 查询详细信息（含产业链及个股）
"""
@router.get("/detail/{sector_id}", summary="根据板块ID查询详细信息")
async def get_detail_by_id(sector_id: int):
    return await hot_sector_service.get_detail_by_id(sector_id=sector_id)
