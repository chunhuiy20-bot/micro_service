import requests


class TwelveDataClient:
    """
    免费 800次/天，需要 API key
    symbol 格式: AAPL, MSFT, 0700:HKEX, 600519:XSHG
    """
    BASE_URL = "https://api.twelvedata.com"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_realtime_price(self, symbol: str) -> dict:
        params = {"symbol": symbol, "apikey": self.api_key}
        data = requests.get(f"{self.BASE_URL}/price", params=params).json()
        print(f"TwelveDataClient 拉取实时数据：{data}")
        return {
            "symbol": symbol,
            "price": float(data.get("price", 0)),
        }

    def get_realtime_prices(self, symbols: list[str]) -> list[dict]:
        """批量获取实时价格，symbols 最多 8 个（免费额度限制）"""
        params = {"symbol": ",".join(symbols), "apikey": self.api_key}
        data = requests.get(f"{self.BASE_URL}/price", params=params).json()
        result = []
        for symbol in symbols:
            item = data.get(symbol, {})
            result.append({
                "symbol": symbol,
                "price": float(item.get("price", 0)),
            })
        return result

    def get_kline(self, symbol: str, interval: str = "1day",
                  start_date: str = "", end_date: str = "", outputsize: int = 100) -> list[dict]:
        """
        interval: 1min 5min 15min 30min 1h 2h 4h 1day 1week 1month
        start_date / end_date 格式: 2024-01-01
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.api_key,
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        data = requests.get(f"{self.BASE_URL}/time_series", params=params).json()
        values = data.get("values", [])
        return [
            {
                "time": v["datetime"],
                "open": float(v["open"]),
                "high": float(v["high"]),
                "low": float(v["low"]),
                "close": float(v["close"]),
                "volume": int(v.get("volume", 0)),
            }
            for v in reversed(values)
        ]

    def get_macd(self, symbol: str, interval: str = "1day",
                 fast: int = 12, slow: int = 26, signal: int = 9,
                 outputsize: int = 100) -> list[dict]:
        """
        interval: 1min 5min 15min 30min 1h 1day 1week 1month
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "fast_period": fast,
            "slow_period": slow,
            "signal_period": signal,
            "outputsize": outputsize,
            "apikey": self.api_key,
        }
        data = requests.get(f"{self.BASE_URL}/macd", params=params).json()
        values = data.get("values", [])
        return [
            {
                "time": v["datetime"],
                "macd": float(v["macd"]),
                "signal": float(v["macd_signal"]),
                "histogram": float(v["macd_hist"]),
            }
            for v in reversed(values)
        ]
