from binance import Client

import config
import numpy as np

class Auxiliary():
    def __init__(self, coin_pair, ex_rate, amount):
        self.coin_pair = coin_pair
        self.amount = amount
        self.ex_rate = ex_rate
        
    def buy_qty_det(self):
        """This function determines how much coins can be bought for a given exchange rate.

        Parameters
        ----------
        self : self
            Self object variable.

        Returns
        ----------
        qty : float
            Quantity of coins that can be bought.
        """
        
        client = config.client
        #ex_rate = client.get_symbol_ticker(symbol=self.coin_pair)["price"]

        return round(self.amount / float(self.ex_rate)) #, 2)
    
    def sell_qty_det(self):
        """This function determines how much coins can be sold for a given exchange rate.

        Parameters
        ----------
        self : self
            Self object variable.

        Returns
        ----------
        qty : float
            Quantity of coins that can be sold.
        """
        
        client = config.client
        #ex_rate = client.get_symbol_ticker(symbol=self.coin_pair)["price"]
        #asset_balance = float(client.get_asset_balance(asset=self.coin_pair.replace("USDT", ""))["free"])

        return round((self.amount / float(self.ex_rate) * 0.998), 2) 
    
   
 
def avg_change_minute(coin_pair):
    """This function computes the average price movement over a 5 minute time frame. 

    Parameters
    ----------
    coin_pair : str
        Coin pair for which the angle is to be computed.
        
    Returns
    ----------
    np.mean : float
        Mean change for the given interval.
    """

    client = config.client
    
    mean_interval = []
    candles = client.get_klines(symbol=coin_pair, interval=Client.KLINE_INTERVAL_1MINUTE)
    for k in range(len(candles)):
        candle = [float(i) for i in candles[-k][1:5]]
        interval = np.max(candle) - np.min(candle)
        mean_interval.append(interval)
    
    return np.mean(mean_interval)


        

