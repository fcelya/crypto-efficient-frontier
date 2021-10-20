import requests
import pandas as pd

def get_crypto(crypto,period='86400'):
    url_base = 'https://api.cryptowat.ch/markets/'
    url_market = 'binance/'
    url_pair = crypto + 'usdt/'
    url_ohlc = 'ohlc?'
    url_periods = 'periods='+period
    
    url = url_base + url_market + url_pair + url_ohlc + url_periods
    r = requests.get(url)
    data = r.json()
    
    data = data['result'][period]
    
    data_df = {'timestamp':[], 'open':[], 'high':[], 'low':[], 'close':[], 'vol':[], 'quotevol':[]}
    index_df = []
    i = 1
    for day in data:
        data_df['timestamp'].append(day[0])
        data_df['open'].append(day[1])
        data_df['high'].append(day[2])
        data_df['low'].append(day[3])
        data_df['close'].append(day[4])
        data_df['vol'].append(day[5])
        data_df['quotevol'].append(day[6])
        index_df.append(i)
        i += 1
    df = pd.DataFrame(data_df, index=index_df)
    return df

