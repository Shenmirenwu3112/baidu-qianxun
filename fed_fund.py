import requests
import pandas as pd
from datetime import datetime

START_TIME = '2018-02-01'
END_TIME = '2025-02-01'
## https://fredaccount.stlouisfed.org/apikeys
API_KEY = '2799e9ff56082e330f1d816ae93a1f87'

# 美联储Fred数据
def get_api_response(series_id: str) -> requests.Response:
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEY}&file_type=json'
    return requests.get(url)

# 美联储的历史利率数据
def get_historical_FederalFundsRate(start_time: str, end_time: str) -> dict:
    series_id = 'EFFR'
    response = get_api_response(series_id)

    if response.status_code == 200:
        data = response.json()
        observations = data['observations']
        
        df = pd.DataFrame(observations)
        df = df[['date', 'value']]
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df[df['date']>=start_time].reset_index(drop=True)
        df['date'] = pd.to_datetime(df['date'])

        full_date_range = pd.date_range(start=start_time, end=end_time, freq='D')
        df_full = pd.DataFrame({'date': full_date_range})
        df = pd.merge(df_full, df, on='date', how='left')
        ## 补齐一些缺失的日期
        df['value'] = df['value'].fillna(method='ffill')
        print(df.head())
        start_date = datetime.strptime(START_TIME, "%Y-%m-%d")
        end_date = datetime.strptime(END_TIME, "%Y-%m-%d")
        print("有所有的对应时间的数据吗？：", (len(df) == (end_date-start_date).days+1))
        print(df.info())
        return df.to_dict(orient='records')
        
    else:
        print("请求失败，状态码:", response.status_code)
        return dict()

# 美联储具体加息或降息时间
def get_historical_FederalFundsRate_changes() -> str:
    series_id = 'DFEDTAR'   # 1982 ~ 2008
    series_id1 = 'DFEDTARU'  # 2008 ~ now (upper)
    series_id2 = 'DFEDTARL'  # 2008 ~ now (lower)

    resp  = get_api_response(series_id)
    respU = get_api_response(series_id1)
    respL = get_api_response(series_id2)

    if resp.status_code==200 and respU.status_code==200 and respL.status_code==200:
        df  = pd.DataFrame(resp.json()['observations'])
        dfU = pd.DataFrame(respU.json()['observations'])
        dfL = pd.DataFrame(respL.json()['observations'])

        for d in (df, dfU, dfL):
            d['date'] = pd.to_datetime(d['date'])
            d['value'] = pd.to_numeric(d['value'], errors='coerce')
        dfU.rename(columns={'value':'upper'}, inplace=True)
        dfL.rename(columns={'value':'lower'}, inplace=True)

        df_range = pd.merge(dfL, dfU, on='date', how='inner')
        df_range['value'] = (df_range['upper'] + df_range['lower'])/2

        df_all = pd.concat([df[['date','value']], df_range[['date','value']]], ignore_index=True)
        df_all.sort_values('date', inplace=True)
        df_all.dropna(inplace=True)

        df_all['change'] = df_all['value'].diff()
        df_all['event']  = df_all['change'].apply(
            lambda x: '加息' if x>0 else ('降息' if x<0 else '无变化')
        )

        df_changes = df_all[df_all['event']!='无变化'].reset_index(drop=True)
        records = df_changes.to_dict(orient='records')
        # only keep last 5
        last5 = records[-5:]

        # format to text
        formatted = "\n".join(
            f"{r['date'].strftime('%Y-%m-%d')}: rate={r['value']:.3f}, change={r['change']:.3f}, event={r['event']}"
            for r in last5
        )
        return "最新5次美联储利率变动：\n" + formatted

    raise ValueError("Failed to fetch Fed Funds rate data")

# print(get_historical_FederalFundsRate_changes())