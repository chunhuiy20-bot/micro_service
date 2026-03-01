import asyncio
from datetime import date
from typing import List
from openai import AsyncOpenAI
from openai.types.responses import EasyInputMessageParam, WebSearchToolParam
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from stock_service.ai_driven_execution.prompt.BasePrompt import BasePrompt
from stock_service.config.ServiceConfig import stock_service_config
from stock_service.schemas.structured_ai_response.HighMomentumSectors import HighMomentumSector, \
    HotSectorAnalyticsResult
from stock_service.service.HotSectorService import hot_sector_service
from common.utils.decorators.AsyncDecorators import async_retry


class HotSectorPredictiveAnalytics:

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=stock_service_config.openai_api_key,
            base_url=stock_service_config.openai_base_url,
        )

    @async_retry(max_retries=3, delay=5)
    async def _fetch_market_news(self, top_n: int) -> str:
        """
        Step 1: 调用 OpenAI web_search 工具搜索今日 A 股市场热点新闻
        """
        today = date.today().isoformat()
        web_searcher = next(p for p in BasePrompt if p["role"] == "web-searcher")
        content = web_searcher["prompt"].format(today=today, top_n=top_n)
        response = await self._client.responses.create(
            model="o4-mini",
            tools=[WebSearchToolParam(type="web_search")],
            input=[EasyInputMessageParam(role="user", content=content)],
        )
        return response.output_text or ""

    async def fetch_today_hot_sectors(self, top_n: int = 5) -> List[HighMomentumSector]:
        """
        两步调用 OpenAI 获取今日热门板块分析结果：
          Step 1 - web_search 抓取今日市场热点新闻摘要
          Step 2 - 基于新闻上下文生成结构化 HighMomentumSector 分析
        :param top_n: 返回板块数量，默认 5 个
        :return: HighMomentumSector 列表，按热度降序
        """
        today = date.today().isoformat()

        news_summary = await self._fetch_market_news(top_n)
        if not news_summary:
            raise ValueError("未获取到市场新闻，终止分析")
        print(f'新闻：{news_summary}')
        sector_user = next(p for p in BasePrompt if p["role"] == "sector_analyst_user")
        user_prompt = sector_user["prompt_with_summary"].format(today=today, news_summary=news_summary, top_n=top_n)
        analyst = next(p for p in BasePrompt if p["role"] == "a_share_sector_analyst")
        response = await self._client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                ChatCompletionSystemMessageParam(role="system", content=analyst["prompt"]),
                ChatCompletionUserMessageParam(role="user", content=user_prompt),
            ],
            response_format=HotSectorAnalyticsResult,
        )

        result = response.choices[0].message.parsed
        return result.sectors


hot_sector_analytics = HotSectorPredictiveAnalytics()


async def periodic_tock_analysis_job():
    result = await hot_sector_analytics.fetch_today_hot_sectors(5)
    print(result)
    today = date.today()
    for sector in result:
        await hot_sector_service.save(sector, today)
    return result

if __name__ == "__main__":
    asyncio.run(periodic_tock_analysis_job())