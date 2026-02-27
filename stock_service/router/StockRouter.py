from fastapi import Query
from common.utils.router.CustomRouter import CustomAPIRouter
from stock_service.service.StockService import stock_service

router = CustomAPIRouter(
    prefix="/api/stock",
    tags=["股票数据服务"],
    auto_log=True,
    logger_name="stock-service",
    log_exclude_args=["api_key"]
)


@router.get("/price", summary="获取实时价格")
async def get_realtime_price(
    symbol: str = Query(..., description="股票代码，如 AAPL / 300750.SZ / 0700.HK"),
    source: str = Query("yfinance", description="数据源: yfinance / alpha_vantage / twelve_data"),
):
    return stock_service.get_realtime_price(symbol=symbol, source=source)


@router.get("/kline", summary="获取历史K线")
async def get_kline(
    symbol: str = Query(..., description="股票代码"),
    source: str = Query("yfinance", description="数据源: yfinance / alpha_vantage / twelve_data"),
    interval: str = Query("1d", description="yfinance: 1m/5m/1h/1d | alpha_vantage: daily/weekly | twelve_data: 1min/1h/1day"),
    period: str = Query("1mo", description="yfinance 专用: 1d/5d/1mo/3mo/6mo/1y"),
    outputsize: int = Query(100, description="alpha_vantage/twelve_data 返回条数"),
    start_date: str = Query("", description="twelve_data 专用，格式: 2024-01-01"),
    end_date: str = Query("", description="twelve_data 专用，格式: 2024-12-31"),
):
    if source == "yfinance":
        return stock_service.get_kline(symbol=symbol, source=source, interval=interval, period=period)
    if source == "alpha_vantage":
        return stock_service.get_kline(symbol=symbol, source=source, interval=interval, outputsize="compact" if outputsize <= 100 else "full")
    # twelve_data
    return stock_service.get_kline(symbol=symbol, source=source, interval=interval,
                                   outputsize=outputsize, start_date=start_date, end_date=end_date)


@router.get("/macd", summary="获取MACD指标")
async def get_macd(
    symbol: str = Query(..., description="股票代码"),
    source: str = Query("yfinance", description="数据源: yfinance / alpha_vantage / twelve_data"),
    interval: str = Query("1d", description="yfinance: 1d | alpha_vantage: daily | twelve_data: 1day"),
    fast: int = Query(12, description="快线周期"),
    slow: int = Query(26, description="慢线周期"),
    signal: int = Query(9, description="信号线周期"),
    outputsize: int = Query(100, description="返回条数（alpha_vantage/twelve_data）"),
):
    if source == "yfinance":
        return stock_service.get_macd(symbol=symbol, source=source, fast=fast, slow=slow, signal=signal)
    if source == "alpha_vantage":
        return stock_service.get_macd(symbol=symbol, source=source, interval=interval, fast=fast, slow=slow, signal=signal)
    # twelve_data
    return stock_service.get_macd(symbol=symbol, source=source, interval=interval,
                                  fast=fast, slow=slow, signal=signal, outputsize=outputsize)
