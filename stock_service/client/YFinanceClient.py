import os

import yfinance as yf
import pandas as pd

PROXY = "http://127.0.0.1:7890"


def _set_proxy():
    os.environ["HTTP_PROXY"] = PROXY
    os.environ["HTTPS_PROXY"] = PROXY


def _clear_proxy():
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)


def _fetch_history(ticker: yf.Ticker, **kwargs) -> pd.DataFrame:
    """先直连，失败后走代理重试"""
    try:
        df = ticker.history(**kwargs)
        if not df.empty:
            return df
    except Exception:
        pass
    # 直连失败，走代理
    _set_proxy()
    try:
        return ticker.history(**kwargs)
    finally:
        _clear_proxy()


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
        df = _fetch_history(ticker, period="1d", interval="1m")
        if df.empty:
            df = _fetch_history(ticker, period="5d", interval="1d")
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

    def get_kline(self, symbol: str, interval: str = "1d", period: str = "1mo") -> list[dict]:
        """
        interval: 1m 5m 15m 30m 1h 1d 1wk 1mo
        period:   1d 5d 1mo 3mo 6mo 1y 2y 5y max
        """
        ticker = yf.Ticker(symbol)
        df = _fetch_history(ticker, period=period, interval=interval)
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
        df = _fetch_history(ticker, period=period, interval="1d")
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
