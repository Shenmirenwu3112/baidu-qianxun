from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
import yfinance as yf
from datetime import datetime, timedelta

def get_fx_summary(ticker: str = 'USDCNY=X') -> str:
    fx = yf.Ticker(ticker)
    # 最新价（最近收盘或实时）
    todays_data = fx.history(period="1d", interval="1m")
    if not todays_data.empty:
        latest_row       = todays_data.dropna().iloc[-1]
        latest_price     = round(latest_row['Close'], 4)
        latest_timestamp = todays_data.dropna().index[-1].to_pydatetime().strftime('%Y-%m-%d %H:%M:%S')
    else:
        latest_price, latest_timestamp = None, None

    # 1 周范围
    one_week_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    data_1w      = fx.history(start=one_week_ago)
    week_high    = data_1w['High'].max()
    week_low     = data_1w['Low'].min()

    # 1 个月范围
    one_month_ago = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    data_1m       = fx.history(start=one_month_ago)
    month_high    = data_1m['High'].max()
    month_low     = data_1m['Low'].min()
    text=f"从{ticker[:3]}兑换{ticker[3:6]}的最新汇率为{latest_price},其更新时间为{latest_timestamp},1周的波动范围为{round(week_low, 4)}~{round(week_high, 4)},1个月的波动范围为{round(month_low, 4)}~{round(month_high, 4)}"
    # base, quote = ticker.split('=')[0], ticker.split('=')[1]
    return text