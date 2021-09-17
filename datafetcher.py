import pandas as pd
from auxiliary import avg_change_minute

import config

def fetch_coinpairs():
    """This function fetches a cleaned dataframe with all tickers. 
    
    All fiat currencies, stable coins and exotic pairs are removed. 
    
    Parameters
    ----------
    client : Binance Object
        Client provides API access. 
    
    Returns
    -------
    df : DataFrame
        DataFrame with coin pairs quoted in USDT. 
    """
    client = config.client
        
    # get and process price information
    df = pd.DataFrame(client.get_all_tickers()).dropna()
    df["price"] = df["price"].astype(float) 
    relevant_coinpairs = ["USDT"] 
    irrelevant_coinpairs = ["STORMUSDT", "LENDUSDT", "USDTUAH", "USDTBRL", "DOWN", "UP", "BULL", 
                            "USDTBIDR","BEAR", "BCHSVUSDT", "USDTGYEN", "BCCUSDT", "BCHSVUSDT",
                           "ERDUSDT", "USDTIDRT", "DAIUSDT", "AUDUSDT", "USDTNGN", "USDTZAR",
                           "PAXUSDT", "USDSBUSDT", "PAXUSDT", "USDTDAI", "EPSUSDT"]
    
    # remove irrelevant coins
    for coinpair in relevant_coinpairs:
        df = df[df["symbol"].apply(lambda x: True if coinpair in x else False)]
        
    for coin_pair in df["symbol"]:
        # if irrelevant coin pair in coin pair, remove from df
        for ir_coin_pair in irrelevant_coinpairs:
            if ir_coin_pair in coin_pair:
                df = df[df["symbol"]!=coin_pair]

    # reset index and return 
    return df.reset_index(drop=True)

def coin_pair_selector(df, trade_margin, amount = 10):
    """This functions selects the coin pairs that will most likely result in a succesfull trade.
    
    The delta metric measures how likely it will be that the necessary movement will be achieved
    within a 1 minute time frame -- the closer to 0, the more likely this will be. 
    
    Parameters
    ----------
    df : DataFrame
        DataFrame with the relevant coin pairs.
    trade_margin: float, default : 0.01
        The desired percentage of profit.
    amount : int, default 10
        The amount of money (USDT) invested in the trade.
    
    Returns
    -------
    df : DataFrame
        DataFrame with coin pairs quoted in USDT. 
    """

    df["up_by"] = df["price"] * config.ROI # trade margin (or ROI) is the percentage by which the price should go up
    df["target_price"] = df["up_by"] + df["price"]

    df["#coins"] = config.USDT_amount / df["price"] 
    df["avg_chg_minute"] = df["symbol"].apply(avg_change_minute)
    df["Δ1"] = abs((df["avg_chg_minute"] - df["up_by"]) / df["avg_chg_minute"])

    df = df.sort_values(by="Δ1", ascending=True)
    #df = df[df["Δ1"] < 10]
    
    return df