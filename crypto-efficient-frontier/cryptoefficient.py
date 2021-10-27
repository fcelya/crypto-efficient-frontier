import requests
import pandas as pd
import numpy as np
from scipy.optimize import minimize

def get_crypto(crypto,period='86400'):
    '''
    Parameters
    ----------
    crypto : String
        Ticker for the crypto.
    period : String, optional
        seconds between datapoints. The default is '86400' which stands for 1 day.

    Returns
    -------
    df : DataFrame
        Contains timestamp, open, high, low, close, volume, quotevolume.

    '''
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

def returns(df):
    return df['close'].pct_change()

def annualize_rets(r, periods_per_year=365):
    """
    Parameters
    ----------
    r : pd.DataFrame
        Contains the returns of the different assets.
    periods_per_year : float, optional
        Annual frequency of the returns data provided in r. The default is 365.

    Returns
    -------
    pd.Series
        Annualized returns for each asset.

    """
    compounded_growth = (1+r).prod()
    n_periods = r.shape[0]
    return compounded_growth**(periods_per_year/n_periods)-1

def portfolio_return(weights, returns):
    """
    Parameters
    ----------
    weights : np.Array or Nx1 matrix
        Weights for each asset.
    returns : np.Array or Nx1 matrix
        Returns of each asset.

    Returns
    -------
    np.float64
        The return of the specified portfolio.

    """
    return weights.T @ returns

def cryptodict_dfrets(dic):
    """
    Parameters
    ----------
    dic : dict
        Keys: name of asset. Values: dataframe cointaining the data as specified in get_crypto().

    Returns
    -------
    rets_df : pd.DataFrame
        Contains the returns for the different assets for every period.

    """
    header = dic.keys()
    rets_list = []
    for c in dic:
        rets_list.append(dic[c]['close'].pct_change())
    rets_df = pd.concat(rets_list, axis=1, keys=header)
    
    return rets_df

def portfolio_vol(weights, covmat):
    """
    Parameters
    ----------
    weights : np.Array or Nx1 matrix
        Weights for each asset.
    covmat : pd.DataFrame
        Covariance matrix for the assets.

    Returns
    -------
    np.float64
        Total volatility of portfolio.

    """
    return (weights.T @ covmat @ weights)**0.5

def minimize_vol(target_return, cryptos):
    """
    ATTENTION: It calls the api for data, so daily limit may be reached if called too much
    
    Parameters
    ----------
    target_return : float
        Desired return for the portfolio.
    cryptos : list
        List of tickers of cryptos in portfolio.

    Returns
    -------
    dict
        Gives the desired weight associated to each ticker

    """    
    n = len(cryptos)
    crypto_dict = {}
    for c in cryptos:
        crypto_dict[c] = get_crypto(c)

    rets_df = cryptodict_dfrets(crypto_dict)
    
    ann_rets = annualize_rets(rets_df)
    cov = rets_df.cov()
    
    init_guess = np.repeat(1/n, n)
    bounds = ((0.0, 1.0),) * n 
    
    weights_sum_to_1 = {'type': 'eq',
                        'fun': lambda weights: np.sum(weights) - 1
    }
    return_is_target = {'type': 'eq',
                        'args': (rets_df,),
                        'fun': lambda weights, rets_df: target_return - portfolio_return(weights,ann_rets)
    }
    weights = minimize(portfolio_vol, init_guess,
                       args=(cov,), method='SLSQP',
                       options={'disp': False},
                       constraints=(weights_sum_to_1,return_is_target),
                       bounds=bounds)
    i = 0
    result = {}
    
    for x in weights.x:
        result[cryptos[i]] = x
        i += 1
        
    return result