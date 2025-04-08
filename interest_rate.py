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
def get_historical_FederalFundsRate_changes() -> dict:
    series_id = 'DFEDTAR'   # 1982 ~ 2008
    series_id1 = 'DFEDTARU'  # 2008 ~ now
    series_id2 = 'DFEDTARL'  # 2008 ~ now

    response = get_api_response(series_id)
    response_upper = get_api_response(series_id1)
    response_lower = get_api_response(series_id2)

    if response.status_code == 200 and response_upper.status_code == 200 and response_lower.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['observations'])
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        data1 = response_upper.json()
        df_upper = pd.DataFrame(data1['observations'])
        
        data2 = response_lower.json()
        df_lower = pd.DataFrame(data2['observations'])

        df_upper['date'] = pd.to_datetime(df_upper['date'])
        df_lower['date'] = pd.to_datetime(df_lower['date'])
        df_upper['value'] = pd.to_numeric(df_upper['value'], errors='coerce')
        df_lower['value'] = pd.to_numeric(df_lower['value'], errors='coerce')
        df_upper.rename(columns={'value': 'upper'}, inplace=True)
        df_lower.rename(columns={'value': 'lower'}, inplace=True)

        df_range = pd.merge(df_lower, df_upper, on='date', how='inner')
        df_range['value'] = (df_range['upper'] + df_range['lower']) / 2

        df = pd.concat([df[['date','value']],df_range[['date','value']]], ignore_index=True)
        df.sort_values('date', inplace=True)
        df.dropna(inplace=True)
        
        df['change'] = df['value'].diff()
        df['event'] = df['change'].apply(lambda x: '加息' if x > 0 else ('降息' if x < 0 else '无变化'))

        rate_change_df = df[df['event'] != '无变化'].copy()
        rate_change_df = rate_change_df.reset_index(drop=True)
        print(rate_change_df.head())
        return rate_change_df.to_dict(orient='records')
    else:
        print("请求失败，状态码:", response_upper.status_code)
        print("请求失败，状态码:", response_lower.status_code)
        return dict()


print(get_historical_FederalFundsRate_changes())