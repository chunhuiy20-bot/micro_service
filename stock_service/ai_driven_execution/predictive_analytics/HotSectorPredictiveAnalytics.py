import asyncio
from datetime import date
from typing import List
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from stock_service.config.ServiceConfig import stock_service_config
from stock_service.schemas.structured_ai_response.HighMomentumSectors import HighMomentumSector


class HotSectorAnalyticsResult(BaseModel):
    """OpenAI 结构化输出包装器"""
    sectors: List[HighMomentumSector] = Field(..., description="今日热门板块列表，按热度降序排列")


class HotSectorPredictiveAnalytics:

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=stock_service_config.openai_api_key,
            base_url=stock_service_config.openai_base_url,
        )

    async def _fetch_market_news(self) -> str:
        """
        Step 1: 调用 OpenAI web_search 工具搜索今日 A 股市场热点新闻
        若 web_search 不可用则返回空字符串，由后续步骤降级处理
        """
        today = date.today().isoformat()
        try:

            response = await self._client.responses.create(
                model="o4-mini",
                tools=[{
                    "type": "web_search",
                    "user_location": {
                        "type": "approximate",
                        "country": "CN",
                        "city": "Beijing",
                        "region": "Beijing",
                    }
                }],
                input=[
                    {
                        "role": "user",
                        "content":
                            f"今天是 {today}，请搜索以下内容并给出简洁摘要（500字以内）：1. A股今日涨幅最大的板块及主要原因 2. 近期重要政策利好或产业催化事件 3. 主力资金净流入最多的行业方向 4. 机构最新研报重点推荐的赛道"

                    }
                ],
            )

            # response = await self._client.chat.completions.create(
            #     model="o4-mini",
            #     tools=[{
            #         "type": "web_search"
            #     }],
            #     input=[
            #         {
            #             "role": "user",
            #             "content": (
            #                 f"今天是 {today}，请搜索以下内容并给出简洁摘要（500字以内）：\n"
            #                 "1. A股今日涨幅最大的板块及主要原因\n"
            #                 "2. 近期重要政策利好或产业催化事件\n"
            #                 "3. 主力资金净流入最多的行业方向\n"
            #                 "4. 机构最新研报重点推荐的赛道"
            #             )
            #         }
            #     ]
            # )
            return response.output_text or ""
        except Exception:
            return ""

    async def fetch_today_hot_sectors(self, top_n: int = 5) -> List[HighMomentumSector]:
        """
        两步调用 OpenAI 获取今日热门板块分析结果：
          Step 1 - web_search 抓取今日市场热点新闻摘要
          Step 2 - 基于新闻上下文生成结构化 HighMomentumSector 分析
        :param top_n: 返回板块数量，默认 5 个
        :return: HighMomentumSector 列表，按热度降序
        """
        today = date.today().isoformat()

        news_summary = await self._fetch_market_news()
        print(f"新闻： {news_summary}")
        news_context = (
            f"以下是今日（{today}）A股市场最新热点新闻摘要，请结合这些信息进行分析：\n\n"
            f"{news_summary}\n\n"
            if news_summary
            else f"（未能获取实时新闻，请基于你的知识库对 {today} 市场热点进行分析）\n\n"
        )

        prompt = (
            f"{news_context}"
            f"请分析当前 A 股市场热度最高的 {top_n} 个板块，要求：\n"
            "1. 每个板块包含完整的上游、中游、下游产业链分析\n"
            "2. 每个环节列举 2-3 只代表性个股，给出入选理由和动能评分（0-100）\n"
            "3. heat_index 综合资金流入、涨幅、舆论热度评估（0-100）\n"
            "4. catalysts 结合上方新闻列举真实催化剂事件\n"
            "5. 按 heat_index 从高到低排列"
        )

        response = await self._client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是A股专业的股票市场分析师，擅长识别市场热点板块和产业链投资机会。"},
                {"role": "user", "content": prompt},
            ],
            response_format=HotSectorAnalyticsResult,
        )

        result = response.choices[0].message.parsed
        print(result)
        return result.sectors


hot_sector_analytics = HotSectorPredictiveAnalytics()


if __name__ == "__main__":
    asyncio.run(hot_sector_analytics.fetch_today_hot_sectors(5))
