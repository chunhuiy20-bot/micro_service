import json
from datetime import date
from typing import List
from common.schemas.CommonResult import Result
from common.utils.decorators.AsyncDecorators import async_retry
from common.utils.decorators.WithRepoDecorators import with_repo
from stock_service.model.HotSector import HotSector
from stock_service.model.HotSectorChainLink import HotSectorChainLink
from stock_service.model.HotSectorStock import HotSectorStock
from stock_service.repository.HotSectorRepository import HotSectorRepository
from stock_service.repository.HotSectorChainLinkRepository import HotSectorChainLinkRepository, hot_sector_chain_link_repo
from stock_service.repository.HotSectorStockRepository import HotSectorStockRepository, hot_sector_stock_repo
from stock_service.schemas.structured_ai_response.HighMomentumSectors import HighMomentumSector, ChainLink
from stock_service.schemas.response.HotSectorResponseSchemas import (
    HotSectorBriefResponse, HotSectorDetailResponse, HotSectorChainLinkResponse, HotSectorStockResponse
)


class HotSectorService:

    async def _save_chain_link(self, sector_id: int, chain_type: str, link: ChainLink):
        """保存一个产业链环节及其个股"""
        chain_record = HotSectorChainLink(
            sector_id=sector_id,
            chain_type=chain_type,
            stage=link.stage,
            description=link.description,
        )
        saved_link = await hot_sector_chain_link_repo.save(chain_record)

        for stock in link.key_stocks:
            stock_record = HotSectorStock(
                chain_link_id=saved_link.id,
                symbol=stock.symbol,
                name=stock.name,
                reason=stock.reason,
                momentum_score=stock.momentum_score,
            )
            await hot_sector_stock_repo.save(stock_record)

    async def _delete_by_sector_id(self, sector_id: int):
        """删除某板块下所有环节及个股"""
        link_wrapper = hot_sector_chain_link_repo.query_wrapper().eq("sector_id", sector_id)
        links = await hot_sector_chain_link_repo.list(link_wrapper)
        for link in links:
            stock_wrapper = hot_sector_stock_repo.query_wrapper().eq("chain_link_id", link.id)
            stocks = await hot_sector_stock_repo.list(stock_wrapper)
            for s in stocks:
                await hot_sector_stock_repo.remove_by_id(s.id)
            await hot_sector_chain_link_repo.remove_by_id(link.id)

    @async_retry(max_retries=3, delay=3)
    @with_repo(HotSectorRepository, db_name="main")
    async def save(self, sector_repo: HotSectorRepository, data: HighMomentumSector, record_date: date) -> Result[bool]:
        """
        保存 AI 返回的热门板块数据，已存在则覆盖更新
        :param data: AI 返回的 HighMomentumSector 结构
        :param record_date: 采集日期
        """
        try:
            wrapper = sector_repo.query_wrapper().eq("sector_name", data.sector_name).eq("record_date", record_date)
            existing = await sector_repo.get_one(wrapper)

            if existing:
                await sector_repo.update_by_id_selective(existing.id, {
                    "narrative": data.narrative,
                    "heat_index": data.heat_index,
                    "catalysts": json.dumps(data.catalysts, ensure_ascii=False),
                    "risk_tips": data.risk_tips,
                })
                await self._delete_by_sector_id(existing.id)
                sector_id = existing.id
            else:
                record = HotSector(
                    record_date=record_date,
                    sector_name=data.sector_name,
                    narrative=data.narrative,
                    heat_index=data.heat_index,
                    catalysts=json.dumps(data.catalysts, ensure_ascii=False),
                    risk_tips=data.risk_tips,
                )
                saved = await sector_repo.save(record)
                sector_id = saved.id

            await self._save_chain_link(sector_id, "upstream", data.upstream)
            await self._save_chain_link(sector_id, "midstream", data.midstream)
            await self._save_chain_link(sector_id, "downstream", data.downstream)

            return Result.success(True)
        except Exception as e:
            return Result.fail(f"保存热门板块失败: {str(e)}")

    @async_retry(max_retries=3, delay=3)
    @with_repo(HotSectorRepository, db_name="main")
    async def list_today_brief(self, sector_repo: HotSectorRepository) -> Result[List[HotSectorBriefResponse]]:
        """查询今日热门板块基础信息列表"""
        today = date.today()
        wrapper = sector_repo.query_wrapper().eq("record_date", today).order_by_desc("heat_index")
        records = await sector_repo.list(wrapper)
        return Result.success([HotSectorBriefResponse.model_validate(r) for r in records])

    @async_retry(max_retries=3, delay=3)
    @with_repo(HotSectorRepository, db_name="main")
    async def get_today_detail(self, sector_repo: HotSectorRepository, sector_name: str) -> Result[HotSectorDetailResponse]:
        """查询今日某个热门板块详细信息（含产业链及个股）"""
        today = date.today()
        wrapper = sector_repo.query_wrapper().eq("record_date", today).eq("sector_name", sector_name)
        sector = await sector_repo.get_one(wrapper)
        if not sector:
            return Result.fail(f"今日板块 '{sector_name}' 不存在")

        link_wrapper = hot_sector_chain_link_repo.query_wrapper().eq("sector_id", sector.id)
        links = await hot_sector_chain_link_repo.list(link_wrapper)

        chain_map = {}
        for link in links:
            stock_wrapper = hot_sector_stock_repo.query_wrapper().eq("chain_link_id", link.id)
            stocks = await hot_sector_stock_repo.list(stock_wrapper)
            chain_map[link.chain_type] = HotSectorChainLinkResponse(
                id=link.id,
                chain_type=link.chain_type,
                stage=link.stage,
                description=link.description,
                key_stocks=[HotSectorStockResponse.model_validate(s) for s in stocks],
            )

        detail = HotSectorDetailResponse(
            **HotSectorBriefResponse.model_validate(sector).model_dump(),
            upstream=chain_map.get("upstream"),
            midstream=chain_map.get("midstream"),
            downstream=chain_map.get("downstream"),
        )
        return Result.success(detail)


hot_sector_service = HotSectorService()
