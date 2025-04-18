from __future__ import annotations
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

"""
example: 
    AAPL: EQUITY (股票)
    PCRB: ETF (​交易型开放式指数基金)
    VTSAX: MUTUALFUND (共同基金)
    ^GSPC: INDEX (指数)
    NVDA250411C00105000: OPTIONS (期权)
    CL=F: FUTURES (期货)
    EURUSD=X : CURRENCY (货币)
    BTC-USD: CRYPTOCURRENCY (​加密货币)
"""

TICKER = "AAPL"

START_DATE="2018-01-01"
END_DATE="2025-03-14"
TIME_INTERVAL= "1d"

# 获取指定时间范围的Ticker数据，可以设定时间维度
def get_data(
    ticker: str,
    start_date: str,
    end_date: str,
    time_interval: str,
    proxy: str | dict = None,
) -> dict:
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    temp_df = yf.download(
        ticker, 
        start=start_date,
        end=end_date,
        interval=time_interval,
        proxy=proxy,
        group_by='ticker'
    )
    if isinstance(temp_df.columns, pd.MultiIndex):
        temp_df.columns = temp_df.columns.droplevel(0)
    temp_df["ticker"] = ticker
    return temp_df.to_dict(orient='records')

#print(get_data('CL=F',START_DATE,END_DATE,TIME_INTERVAL))

# 获取Ticker的信息
def get_ticker_info(ticker: str) -> dict:
    ticker = yf.Ticker(ticker=ticker)
    return ticker.get_info()

print()
#print(get_ticker_info(ticker='CL=F'))

from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
import yfinance as yf

app = FastAPI()

TIME_INTERVAL = "1d"  # Assuming daily data, adjust as needed

# Function to get Futures data for the last 7 days and weekly change
def get_futures(future_ticker: str) -> tuple[dict, dict]:
    """
    Fetch the last 7 days of futures data and weekly change percentage.
    """
    # Get data for the ticker
    try:
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Fetch the last 7 days of data
        future_7days_data = get_data(future_ticker, start_date, end_date, TIME_INTERVAL)

        # Calculate weekly change based on the first and last day
        if len(future_7days_data) > 1:
            weekly_change = (future_7days_data[-1]['Close'] / future_7days_data[0]['Open']) - 1
        else:
            weekly_change = 0

        return future_7days_data, weekly_change
    
    except Exception as e:
        print(f"Error fetching data for {future_ticker}: {e}")
        return dict(), dict()

# print(get_futures('CL=F'))


# 获取Ticker代码的类型
def get_ticker_type(ticker: str) -> str:
    return yf.Ticker(ticker=ticker).get_info().get('quoteType','N/A')

# 获取Ticker的新闻
def get_ticker_news(ticker: str) -> list:
    return yf.Ticker(ticker=ticker).get_news(count=10, tab='news', proxy=None)

def get_ticker_cash_flow(ticker: str, freq: str) -> dict:
    """
    freq : "yearly" | "quarterly"
    """
    return yf.Ticker(ticker=ticker).get_insider_transactions()

def get_region_market(region: str)->list:
    market = yf.Market(region)
    status = market.status
    summary = market.summary
    return [status, summary]

# 获取各个行业部门的情况
def get_financial_market(key:str)-> pd.DataFrame:
    """
    key: basic-materials | communication-services | consumer-cyclical |
         consumer-defensive | energy | financial-services | healthcare |
         industrials | real-estate | technology | utilities
    """
    return yf.Sector(key=key).industries

# 寻找同一个行业的竞争对手
def get_competitors_company(ticker:str) -> yf.Sector:
    info = get_ticker_info(ticker)
    quoteType = info.get('quoteType','N/A')
    if quoteType not in 'EQUITY':
        return dict()
    sectorKey = info.get('sectorKey')
    sector = yf.Sector(key=sectorKey)
    return sector

# 返回竞争对手的symbol
def get_competitors_company_symbol(ticker:str) -> dict:
    sector = get_competitors_company(ticker)
    #----------- SKIP ------------#

# 返回竞争对手的ETF代码和名称
def get_competitors_company_ETF(ticker:str) -> dict:
    """
    return dict[str,str] -> symbols , names
    """
    sector = get_competitors_company(ticker)
    return sector.top_etfs

# 返回竞争对手的Mutual Fund代码和名称
def get_competitors_company_MutualFund(ticker:str) -> dict:
    """
    return dict[str,str] -> symbols , names
    """
    sector = get_competitors_company(ticker)
    return sector.top_mutual_funds
