# api.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from typing import Optional
import uvicorn

import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import finance_data as fd
import fed_fund 
import exchg_rate as er
print(1)
app = FastAPI(
    title="Finance Data API",
    description="API that wraps yfinance api",
    version="1.0.0"
)

@app.get("/data/")
async def fetch_data(
    ticker: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    start: str = Query(fd.START_DATE, description="Start date YYYY-MM-DD"),
    end:   str = Query(fd.END_DATE,   description="End date YYYY-MM-DD"),
    interval: str = Query(fd.TIME_INTERVAL, description="Interval (1d, 1wk, etc.)")
):
    """
    Get historical OHLCV data for a ticker.
    """
    try:
        records = fd.get_data(ticker, start, end, interval)
        return {"ticker": ticker, "records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{ticker}/info")
async def ticker_info(ticker: str):
    """
    Get full yfinance .info dict for a ticker.
    """
    try:
        return fd.get_ticker_info(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{ticker}/type")
async def ticker_type(ticker: str):
    """
    Get the quoteType (e.g. EQUITY, FUTURES) for a ticker.
    """
    try:
        return {"ticker": ticker, "type": fd.get_ticker_type(ticker)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{ticker}/news")
async def ticker_news(
    ticker: str,
    count: Optional[int] = Query(10, description="Max news items to return")
):
    """
    Get recent news items for a ticker.
    """
    try:
        news = fd.get_ticker_news(ticker)
        return news[:count]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{ticker}/cash_flow")
async def ticker_cash_flow(
    ticker: str,
    freq: Optional[str] = Query("yearly", description="\"yearly\" or \"quarterly\"")
):
    """
    Get insider transactions (cash flow) for a ticker.
    """
    try:
        return fd.get_ticker_cash_flow(ticker, freq)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/region_market/{region}")
async def region_market(region: str):
    """
    Get market status and summary for a given region code.
    """
    try:
        status, summary = fd.get_region_market(region)
        return {"region": region, "status": status, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sector/{key}/industries")
async def sector_industries(key: str):
    """
    Get industries for a given sector key.
    """
    try:
        df = fd.get_financial_market(key)
        return {"sector": key, "industries": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/competitors/{ticker}/sector")
async def competitors_sector(ticker: str):
    """
    Get the Sector object for an equity ticker.
    """
    sector = fd.get_competitors_company(ticker)
    if not sector:
        raise HTTPException(status_code=404, detail="Not an equity ticker or no sector data")
    info = {
        "sectorKey": sector.key,
        "name": sector.name,
        "top_etfs": sector.top_etfs,
        "top_mutual_funds": sector.top_mutual_funds,
        # you can add more sector attributes if desired
    }
    return info

@app.get("/competitors/{ticker}/etfs")
async def competitors_etfs(ticker: str):
    """
    Get top ETFs for the sector of a given equity ticker.
    """
    etfs = fd.get_competitors_company_ETF(ticker)
    if not etfs:
        raise HTTPException(status_code=404, detail="No ETF data for this ticker/sector")
    return etfs

@app.get("/competitors/{ticker}/mutualfunds")
async def competitors_mutualfunds(ticker: str):
    """
    Get top mutual funds for the sector of a given equity ticker.
    """
    mfs = fd.get_competitors_company_MutualFund(ticker)
    if not mfs:
        raise HTTPException(status_code=404, detail="No mutual fund data for this ticker/sector")
    return mfs

@app.get("/futures/weekly")
async def get_futures_weekly(ticker: str):
    """
    FastAPI route to get the last 7 days of futures data and weekly change.
    - The `ticker` is passed as a query parameter.
    """
    future_7days_data, weekly_change = fd.get_futures(ticker)
    
    if not future_7days_data:
        raise HTTPException(status_code=404, detail="Futures data not found")
    
    return {
        "ticker": ticker,
        "data": future_7days_data,
        "weekly_change": weekly_change
    }

@app.get(
    "/fed-funds/changes",
    response_class=PlainTextResponse,
    summary="最新五次美联储加息/降息事件",
    description="返回最近5次美联储基准利率变动的日期、利率、改变量及事件（加息/降息）"
)
async def fed_funds_rate_changes():
    try:
        text = fed_fund.get_historical_FederalFundsRate_changes()
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get(
    "/fx/summary",
    response_class=PlainTextResponse,
    summary="外汇汇率摘要",
    description="返回指定货币对的最新汇率及最近 1 周、1 个月的波动区间"
)
async def fx_summary(
    ticker: str = Query(
        "USDCNY=X",
        description="货币对代码，如 USDCNY=X（美元兑人民币）"
    )
):
    """
    查询某货币对（如 USDCNY=X）的最新汇率和波动区间
    """
    try:
        text = er.get_fx_summary(ticker)
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
