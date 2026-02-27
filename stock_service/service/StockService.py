from stock_service.client.YFinanceClient import YFinanceClient
from stock_service.client.AlphaVantageClient import AlphaVantageClient
from stock_service.client.TwelveDataClient import TwelveDataClient
from stock_service.config.ServiceConfig import stock_service_config


class StockService:
    """
    统一股票数据接口
    - yfinance: 免费，无需 key，全球股票
    - alpha_vantage: 25次/天，主要美股/加密货币
    - twelve_data: 800次/天，全球股票
    """

    def __init__(self):
        self._yf = YFinanceClient()
        self._av = AlphaVantageClient(stock_service_config.alpha_vantage_key) if stock_service_config.alpha_vantage_key else None
        self._td = TwelveDataClient(stock_service_config.twelve_data_key) if stock_service_config.twelve_data_key else None

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
        raise ValueError(f"未知数据源: {source}，可选: yfinance / alpha_vantage / twelve_data")

    def get_realtime_price(self, symbol: str, source: str = "yfinance") -> dict:
        return self._get_source(source).get_realtime_price(symbol)

    def get_kline(self, symbol: str, source: str = "yfinance", **kwargs) -> list[dict]:
        return self._get_source(source).get_kline(symbol, **kwargs)

    def get_macd(self, symbol: str, source: str = "yfinance", **kwargs) -> list[dict]:
        return self._get_source(source).get_macd(symbol, **kwargs)


stock_service = StockService()
