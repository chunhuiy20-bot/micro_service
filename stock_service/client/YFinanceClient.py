import yfinance as yf
import pandas as pd

PROXY = "http://127.0.0.1:7890"


class YFinanceClient:
    """
    免费，无需 API key
    symbol 格式:
      美股: AAPL
      深交所: 300750.SZ
      上交所: 600519.SS
      港股: 0700.HK
    """

    def get_realtime_price(self, symbol: str) -> dict:
        ticker = yf.Ticker(symbol)
        df = pd.DataFrame()
        try:
            df = ticker.history(period="1d", interval="1m", proxy=PROXY)
            if df.empty:
                df = ticker.history(period="5d", interval="1d", proxy=PROXY)
        except Exception:
            pass
        if df.empty:
            return {"symbol": symbol, "price": None, "error": "no data"}
        last = df.iloc[-1]
        return {
            "symbol": symbol,
            "price": round(float(last["Close"]), 4),
            "open": round(float(last["Open"]), 4),
            "high": round(float(last["High"]), 4),
            "low": round(float(last["Low"]), 4),
            "volume": int(last["Volume"]),
        }

    def get_realtime_prices(self, symbols: list[str]) -> list[dict]:
        """批量获取实时价格，一次请求拉取所有 symbol"""
        df = pd.DataFrame()
        try:
            df = yf.download(symbols, period="1d", interval="1m", group_by="ticker",
                             auto_adjust=True, progress=False, proxy=PROXY)
        except Exception:
            pass

        result = []
        for symbol in symbols:
            try:
                sub = df if len(symbols) == 1 else df[symbol]
                if sub.empty:
                    result.append({"symbol": symbol, "price": None, "error": "no data"})
                    continue
                last = sub.iloc[-1]
                close = round(float(last["Close"]), 4)
                open_price = round(float(last["Open"]), 4)
                change_percent = round((close - open_price) / open_price * 100, 2) if open_price else None
                result.append({
                    "symbol": symbol,
                    "price": close,
                    "open": open_price,
                    "high": round(float(last["High"]), 4),
                    "low": round(float(last["Low"]), 4),
                    "volume": int(last["Volume"]),
                    "change_percent": change_percent,
                })
            except Exception as e:
                result.append({"symbol": symbol, "price": None, "error": str(e)})
        return result

    def get_kline(self, symbol: str, interval: str = "1d", period: str = "1mo") -> list[dict]:
        """
        interval: 1m 5m 15m 30m 1h 1d 1wk 1mo
        period:   1d 5d 1mo 3mo 6mo 1y 2y 5y max
        """
        ticker = yf.Ticker(symbol)
        df = pd.DataFrame()
        try:
            df = ticker.history(period=period, interval=interval, proxy=PROXY)
        except Exception:
            pass
        if df.empty:
            return []
        df.index = df.index.astype(str)
        return (
            df[["Open", "High", "Low", "Close", "Volume"]]
            .rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
            .reset_index()
            .rename(columns={"Date": "time", "Datetime": "time"})
            .to_dict(orient="records")
        )

    def get_macd(self, symbol: str, period: str = "6mo",
                 fast: int = 12, slow: int = 26, signal: int = 9) -> list[dict]:
        ticker = yf.Ticker(symbol)
        df = pd.DataFrame()
        try:
            df = ticker.history(period=period, interval="1d", proxy=PROXY)
        except Exception:
            pass
        if df.empty:
            return []
        close = df["Close"]
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        df.index = df.index.astype(str)
        return [
            {
                "time": t,
                "macd": round(float(macd_line[t]), 4),
                "signal": round(float(signal_line[t]), 4),
                "histogram": round(float(histogram[t]), 4),
            }
            for t in df.index
        ]
