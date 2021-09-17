import math
import numpy as np
import pandas as pd

from binance import Client
import config

from scipy.stats import norm
import seaborn as sns
from scipy.stats import t
from statsmodels.distributions.mixture_rvs import mixture_rvs
import statsmodels.api as sm
from scipy import stats
from scipy.stats import gaussian_kde
from scipy.stats import norm

import re

def getagnle(coin_pair, time_span="1MINUTE"):
    """This function estimates the angle in radians in a given time interval.

    Parameters
    ----------
    coin_pair : str
        Coin pair for which the angle is to be computed.
    time_span : str, default : "1MINUTE"
        Interval time span.
    Returns
    -------
    angle : float
        Angle in radians.
    """
    client = config.client
    
    if time_span == "1MINUTE":
        candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_1MINUTE)

    elif time_span == "5MINUTE":
        candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_5MINUTE)

    elif time_span == "15MINUTE":
        candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_15MINUTE)

    elif time_span == "30MINUTE":
        candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_30MINUTE)
    else:
        candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_1MINUTE)

    time_series = [candle[1] for candle in candles]  # get open price per n minutes
    time_series = [float(i) for i in list(reversed(time_series))]  # reverse

    # compute angle in radians
    p2_y = time_series[0]
    p1_y = time_series[1]

    deltay = p2_y - p1_y
    deltax = 1  # set to 1 for 1 interval

    angle = math.atan2(deltay, deltax)  # angle in radians
    
    return angle
    
def get_SMA(coin_pair = "VETUSDT"):
    """This function computes the SMA (simple moving average) and ExMA (exponential MA)

    Parameters
    ----------
    coin_pair : str
        Coin pair for which the SMA is to be computed.
        
    Returns
    -------
    SMA_df : DataFrame
        DataFrame with the Moving Average values. 
    """
    
    client = config.client
    
    # get candle sticks
    candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_1MINUTE)
    
    # convert open prices to list
    time_series = [candle[1] for candle in candles] # get open price per n minutes
    time_series = [float(i) for i in list(time_series)]  

    # create df
    time_series = pd.DataFrame(time_series, columns=["price"])
    time_series["SMA(7)"] = time_series["price"].rolling(7, min_periods=1).mean()
    time_series["SMA(25)"] = time_series["price"].rolling(25, min_periods=1).mean()
    time_series["SMA(99)"] = time_series["price"].rolling(99, min_periods=1).mean()
    time_series["ExMA"] = time_series["price"].ewm(alpha=0.3, adjust=False).mean()
    
    return time_series

def price_probability(coin_pair, percentile = 0.95, hours = 1):
    """This determines the likelyhood of hitting the estimated sell price. 

    Based on the price movements in the last ~8.3 hours, a probability value
    will be computed, taking the assumed sell price as its input. 

    N.B. This procedure assumes a t-distribution per proxy. Often, the real
    unerlying is different! Testing for high probability values is advised! 

    Parameters
    ----------
    coin_pair : str
        Coin pair for which the SMA is to be computed.
    ROI : float
        The desired ROI to be made on coin.
    percentile : float, default : 0.75
        The percentile in which the sell price must be.
    hours : int
        Hours determines how far to go back in time to approximate the distribution.
    Returns
    -------
    status : int
        Status to determine if the conditions were met. 1 if True, otherwise 0.
    """
    client = config.client

    candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_1MINUTE)
    current_price = float(re.sub("0{3,}", "", client.get_symbol_ticker(symbol=coin_pair)["price"]))
    time_series = [candle[1] for candle in candles] # get open price per n minutes
    time_series = [float(i) for i in list(time_series)]  
    time_series = time_series[499-(60*hours):499]   # get hourly values 
    sell_price = current_price * config.ROI

    # approximate dist. using normal
    normal = norm(loc = np.mean(time_series), scale = np.std(time_series))
    cut_off = normal.ppf(percentile)      # get cut-off for 99th percentile
    
    # check if sell < cut_off, which can happen from time to time
    if cut_off < sell_price:
        return 0

    # check if estimated sell price is too high 
    elif sell_price > cut_off:
        return 1
    else:
        return 0
    
def hit_rate(coin_pair, hours = 1):
    """This determines whether the selling exchange rate has already been met
    within the last hour. The purpose of this function is to reduce the possibility
    of buying at a peak moment. 

    Parameters
    ----------
    coin_pair : str
        Coin pair for which the SMA is to be computed.
    hours : int
        Hours determines how far to go back in time to approximate the distribution.
    Returns
    -------
    hit rate : float
        Relative frquency of the sell price.
    """
    adjust_multiplier = (config.ROI * 2) - 2   # adjust for missing coins, add. costs etc.

    client = config.client

    candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_1MINUTE)
    current_price = float(re.sub("0{3,}", "", client.get_symbol_ticker(symbol=coin_pair)["price"]))
    time_series = [candle[1] for candle in candles] # get open price per n minutes
    time_series = [float(i) for i in list(time_series)]  
    time_series = time_series[499-(60*hours):499]   # get hourly values 
    sell_price = current_price * (config.ROI + adjust_multiplier)

    hit_rate = [i for i in time_series if i > sell_price] 
    hit_rate = len(hit_rate)/(60 * hours)
    
    return hit_rate