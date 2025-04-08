from __future__ import annotations
import pandas as pd
import yfinance as yf

START_DATE="2018-01-01"
END_DATE="2025-03-14"
TIME_INTERVAL= "1D"

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

print(get_data("^GSPC",START_DATE,END_DATE,TIME_INTERVAL))


