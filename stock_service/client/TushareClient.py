import tushare as ts
import pandas as pd
from datetime import date, timedelta


class TushareClient:
    """
    需要 token（tushare.pro 注册获取），中国 A股专用
    symbol 格式:
      深交所: 300750.SZ
      上交所: 600519.SH（注意: yfinance 用 .SS，tushare 用 .SH）
      港股:   00700.HK（需要较高积分）
    """

    def __init__(self, token: str):
        ts.set_token(token)
        self.pro = ts.pro_api(token)

    def _to_ts_code(self, symbol: str) -> str:
        """yfinance 的 .SS 转为 tushare 的 .SH"""
        return symbol.replace(".SS", ".SH")

    def _to_code(self, symbol: str) -> str:
        """300750.SZ → 300750，用于旧版实时接口"""
        return symbol.split(".")[0]

    def _fmt_date(self, d: str) -> str:
        """YYYY-MM-DD → YYYYMMDD"""
        return d.replace("-", "")

    def _parse_date(self, d: str) -> str:
        """YYYYMMDD → YYYY-MM-DD"""
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"

    def get_realtime_price(self, symbol: str) -> dict:
        """交易时间用 get_realtime_quotes，非交易时间回退到最近日线收盘价"""
        symbol = symbol.strip()
        code = self._to_code(symbol)
        try:
            df = ts.get_realtime_quotes(code)
            if df is not None and not df.empty:
                row = df.iloc[0]
                price = float(row["trade"])
                open_price = float(row["open"])
                if price > 0:
                    change_percent = round((price - open_price) / open_price * 100, 2) if open_price else None
                    return {
                        "symbol": symbol,
                        "price": price,
                        "open": open_price,
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "volume": int(float(row["volume"])),
                        "change_percent": change_percent,
                    }
        except Exception:
            pass

        # 非交易时间或实时接口失败，取最近一个交易日收盘价
        try:
            ts_code = self._to_ts_code(symbol)
            df = self.pro.daily(ts_code=ts_code, limit=1)
            if df is not None and not df.empty:
                row = df.iloc[0]
                return {
                    "symbol": symbol,
                    "price": float(row["close"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "volume": int(float(row["vol"]) * 100),
                    "change_percent": round(float(row["pct_chg"]), 2),
                }
        except Exception as e:
            return {"symbol": symbol, "price": None, "error": str(e)}

        return {"symbol": symbol, "price": None, "error": "no data"}

    def get_realtime_prices(self, symbols: list[str]) -> list[dict]:
        """批量获取实时价格，一次请求拉取所有 symbol"""
        symbols = [s.strip() for s in symbols]
        codes = [self._to_code(s) for s in symbols]
        try:
            df = ts.get_realtime_quotes(codes)
            if df is None or df.empty:
                return [{"symbol": s, "price": None, "error": "no data"} for s in symbols]
            code_to_symbol = {self._to_code(s): s for s in symbols}
            result = []
            for _, row in df.iterrows():
                symbol = code_to_symbol.get(str(row["code"]), str(row["code"]))
                price = float(row["trade"])
                open_price = float(row["open"])
                change_percent = round((price - open_price) / open_price * 100, 2) if open_price else None
                result.append({
                    "symbol": symbol,
                    "price": price,
                    "open": open_price,
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "volume": int(float(row["volume"])),
                    "change_percent": change_percent,
                })
            return result
        except Exception as e:
            return [{"symbol": s, "price": None, "error": str(e)} for s in symbols]

    def get_kline(self, symbol: str, interval: str = "daily",
                  start_date: str = "", end_date: str = "", outputsize: int = 100) -> list[dict]:
        """
        interval: daily（目前只支持日线）
        start_date / end_date 格式: YYYY-MM-DD
        outputsize: 最多返回条数
        """
        ts_code = self._to_ts_code(symbol)
        today_str = date.today().strftime("%Y%m%d")

        if start_date:
            start = self._fmt_date(start_date)
        else:
            start = (date.today() - timedelta(days=outputsize * 2)).strftime("%Y%m%d")
        end = self._fmt_date(end_date) if end_date else today_str

        df = self.pro.daily(ts_code=ts_code, start_date=start, end_date=end)
        if df is None or df.empty:
            return []

        df = df.sort_values("trade_date").tail(outputsize)
        return [
            {
                "time": self._parse_date(str(row["trade_date"])),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": int(float(row["vol"]) * 100),
            }
            for _, row in df.iterrows()
        ]

    def get_macd(self, symbol: str, period: str = "6mo",
                 fast: int = 12, slow: int = 26, signal: int = 9) -> list[dict]:
        end = date.today().strftime("%Y-%m-%d")
        start = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")
        klines = self.get_kline(symbol, start_date=start, end_date=end, outputsize=500)
        if not klines:
            return []
        close = pd.Series([k["close"] for k in klines])
        times = [k["time"] for k in klines]
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return [
            {
                "time": times[i],
                "macd": round(float(macd_line.iloc[i]), 4),
                "signal": round(float(signal_line.iloc[i]), 4),
                "histogram": round(float(histogram.iloc[i]), 4),
            }
            for i in range(len(times))
        ]