import requests


class AlphaVantageClient:
    """
    免费 25次/天，需要 API key
    symbol 格式: AAPL, IBM（主要支持美股）
    """
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_realtime_price(self, symbol: str) -> dict:
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.api_key}
        data = requests.get(self.BASE_URL, params=params).json()
        print(f"获取数据：{data}")
        q = data.get("Global Quote", {})
        return {
            "symbol": symbol,
            "price": float(q.get("05. price", 0)),
            "open": float(q.get("02. open", 0)),
            "high": float(q.get("03. high", 0)),
            "low": float(q.get("04. low", 0)),
            "volume": int(q.get("06. volume", 0)),
            "change_percent": q.get("10. change percent", ""),
        }

    def get_realtime_prices(self, symbols: list[str]) -> list[dict]:
        """批量获取实时价格（逐个请求，注意免费版每日 25 次限额）"""
        return [self.get_realtime_price(symbol) for symbol in symbols]

    def get_kline(self, symbol: str, interval: str = "daily", outputsize: str = "compact") -> list[dict]:
        """
        interval: daily / weekly / monthly
        outputsize: compact(最近100条) / full(全量)
        """
        func_map = {
            "daily": "TIME_SERIES_DAILY",
            "weekly": "TIME_SERIES_WEEKLY",
            "monthly": "TIME_SERIES_MONTHLY",
        }
        params = {
            "function": func_map.get(interval, "TIME_SERIES_DAILY"),
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self.api_key,
        }
        data = requests.get(self.BASE_URL, params=params).json()
        key = [k for k in data if "Time Series" in k]
        if not key:
            return []
        series = data[key[0]]
        return [
            {
                "time": date,
                "open": float(v["1. open"]),
                "high": float(v["2. high"]),
                "low": float(v["3. low"]),
                "close": float(v["4. close"]),
                "volume": int(v["5. volume"]),
            }
            for date, v in sorted(series.items())
        ]

    def get_macd(self, symbol: str, interval: str = "daily", fast: int = 12, slow: int = 26, signal: int = 9) -> list[dict]:
        """
        interval: 1min 5min 15min 30min 60min daily weekly monthly
        """
        params = {
            "function": "MACD",
            "symbol": symbol,
            "interval": interval,
            "series_type": "close",
            "fastperiod": fast,
            "slowperiod": slow,
            "signalperiod": signal,
            "apikey": self.api_key,
        }
        data = requests.get(self.BASE_URL, params=params).json()
        series = data.get("Technical Analysis: MACD", {})
        return [
            {
                "time": t,
                "macd": float(v["MACD"]),
                "signal": float(v["MACD_Signal"]),
                "histogram": float(v["MACD_Hist"]),
            }
            for t, v in sorted(series.items())
        ]
