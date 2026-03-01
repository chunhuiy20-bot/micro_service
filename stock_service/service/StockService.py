from stock_service.client.YFinanceClient import YFinanceClient
from stock_service.client.AlphaVantageClient import AlphaVantageClient
from stock_service.client.TwelveDataClient import TwelveDataClient
from stock_service.client.TushareClient import TushareClient
from stock_service.config.ServiceConfig import stock_service_config


class StockService:
    """
    统一股票数据接口
    - tushare:       需要 token，A股专用，数据质量最好
    - yfinance:      免费，无需 key，全球股票（需代理）
    - alpha_vantage: 25次/天，主要美股
    - twelve_data:   800次/天，全球股票
    """

    def __init__(self):
        self._yf = YFinanceClient()
        self._av = AlphaVantageClient(stock_service_config.alpha_vantage_key) if stock_service_config.alpha_vantage_key else None
        self._td = TwelveDataClient(stock_service_config.twelve_data_key) if stock_service_config.twelve_data_key else None
        self._ts = TushareClient(stock_service_config.tushare_token) if stock_service_config.tushare_token else None

    def _get_source(self, source: str):
        if source == "yfinance":
            return self._yf
        if source == "alpha_vantage":
            if not self._av:
                raise ValueError("ALPHA_VANTAGE_KEY 未配置")
            return self._av
        if source == "twelve_data":
            if not self._td:
                raise ValueError("TWELVE_DATA_KEY 未配置")
            return self._td
        if source == "tushare":
            if not self._ts:
                raise ValueError("TUSHARE_TOKEN 未配置")
            return self._ts
        raise ValueError(f"未知数据源: {source}，可选: tushare / yfinance / alpha_vantage / twelve_data")

    def get_realtime_price(self, symbol: str, source: str = "yfinance") -> dict:
        return self._get_source(source).get_realtime_price(symbol)

    def get_realtime_prices(self, symbols: list[str], source: str = "yfinance") -> dict[str, dict]:
        """批量获取实时价格，返回 {symbol: price_info} 字典，无数据时依次切换数据源"""
        all_sources = ["tushare", "yfinance", "alpha_vantage", "twelve_data"]
        fallback_order = [source] + [s for s in all_sources if s != source]

        for src in fallback_order:
            try:
                client = self._get_source(src)
            except ValueError:
                continue
            try:
                results = client.get_realtime_prices(symbols)
                print(f"实时价格[{src}]：{results}")
                if any(r.get("price") is not None for r in results):
                    return {r["symbol"]: r for r in results}
            except Exception as e:
                print(f"获取实时价格报错：{e}")
                continue

        return {s: {"symbol": s, "price": None} for s in symbols}

    def get_kline(self, symbol: str, source: str = "yfinance", **kwargs) -> list[dict]:
        return self._get_source(source).get_kline(symbol, **kwargs)

    def get_macd(self, symbol: str, source: str = "yfinance", **kwargs) -> list[dict]:
        return self._get_source(source).get_macd(symbol, **kwargs)


stock_service = StockService()
