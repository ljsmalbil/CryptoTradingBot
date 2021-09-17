from binance import Client
from auxiliary import avg_change_minute

import config
import pandas as pd

def movement_identifier(df, theta = 3):
    """This function aims to identify uptrends. 
    
    Uptrends are defined as support from the moving average criteria. If the support is
    larger than a given threshold, a buy signal will be created. Otherwise 0. 

    Parameters
    ----------
    df : DataFrame
        DataFrame with the Moving Average values.
    theta : int, default : 3. 
        Threshold above which a signal is given. 
    Returns
    -------
    SMA_df : DataFrame
        DataFrame with the Moving Average values. 
    """
    
    # start support at 0
    support = 0

    # check if an uptrend in data is visible (if most recent is larger than earlier)
    if df.loc[499,"SMA(7)"] > df.loc[498,"SMA(7)"]: 
        support += 1

    if df.loc[499,"SMA(25)"] > df.loc[498,"SMA(25)"]: 
        support += 1

    if df.loc[499,"SMA(99)"] > df.loc[498,"SMA(99)"]: 
        support += 1

    if df.loc[499,"ExMA"] > df.loc[498,"ExMA"]: 
        support += 1
                
    if support >= theta:
        return 1
    
    else:
        return 0
    
def mean_reversion(coin_pair):
    """Identifies whether a coin is trading below its 5 minute mean value.
    
    Parameters
    ----------
    coin_pair : str
        Coin pair for which the angle is to be computed.
 
    Returns
    -------
    status : int
        Returns 1 if condition has been met, otherwise 0.
    """
    
    client = config.client
    
    current_price = float(client.get_avg_price(symbol=coin_pair)["price"]) 
    mean_price = float(client.get_symbol_ticker(symbol=coin_pair)["price"])   # check if current price is below mean
     
    if mean_price > current_price:
        return 1
    else: 
        return 0
    
def medium_short_term(coin_pair = "WTCUSDT", timespan = 12):
    """This function aims to identify the medium short term trend. 
    
    If the trend is below 1, there is a decline, if above 1, there is an uptrend. 

    Parameters
    ----------
    coin_pair : str
        Coin pair for which the trend is to be computed.
    timespan : int, default : 12.
        Time span for how far to go back. Default, 12 * 5 minutes (1 hour) 
    Returns
    -------
    trend : float
        Computed trend for the given time span
    """
    
    client = config.client

    # get candle sticks
    candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_5MINUTE)

    # convert open prices to list
    time_series = [candle[1] for candle in candles] # get open price per n minutes
    time_series = [float(i) for i in list(time_series)] # reverse 

    # create df
    time_series = pd.DataFrame(time_series, columns=["price"])
    time_series["SMA(99)"] = time_series["price"].rolling(99, min_periods=1).mean()

    # determine relative trend modality 
    trend = time_series.loc[499,"SMA(99)"] / time_series.loc[499 - timespan,"SMA(99)"]
    
    return trend
