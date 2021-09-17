from calculations import get_SMA, getagnle, price_probability, hit_rate
from signals import movement_identifier, mean_reversion, medium_short_term

import pandas as pd
import config

def opportunity_identifier(df, theta):
    """This function searches for coins pair investment opportunities.  
    
    If all conditions are met, the function will return the coin pair.  
    
    Parameters
    ----------
    df : DataFrame
        DataFrame with all possible coin pairs.
    theta : int, default : 4. 
        Threshold above which a signal is given. 
    
    Returns
    -------
    coin_pair : str
        Coin pair recommendation. 
    """
    
    for coin_pair in df["symbol"]:
        try:
            coins_df = get_SMA(coin_pair)
            # identify signals
            alpha_signal = movement_identifier(coins_df, theta=theta)   # check for upward trends
            beta_signal = getagnle(coin_pair, time_span="3MINUTE")      # check for recent uptick
            gamma_signal = mean_reversion(coin_pair)                    # check if coin is trading below mean
            epsilon_signal = medium_short_term(coin_pair)               # check for medium short term uptrend
            zeta_signal = medium_short_term(coin_pair, timespan = 2)    # check for medium short term uptrend
            eta_signal = 1 #hit_rate(coin_pair)  #price_probability(coin_pair, percentile = 0.75)# check for likelihood of going up
            
#             if eta_signal >= 0.004:
#                 print(eta_signal)
#                 print(coin_pair)
            
            # buy if long term cond. are right as well as short term
            if alpha_signal == 1 and beta_signal > 0 and gamma_signal == 1 and epsilon_signal > 1.0005 and zeta_signal > 1.001 and eta_signal >= 0.004:
                
                print(coin_pair)
                print("Alpha Signal: ", str(alpha_signal))
                print("Beta Signal: ", str(beta_signal))
                print("Gamma Signal: ", str(gamma_signal))
                print("Epsilon Signal: ", str(epsilon_signal))
                print("Zeta Signal: ", str(zeta_signal))
                print("Eta Signal: ", str(eta_signal))
                                
                return coin_pair

        except KeyError:
            print(f"ERROR: Key error detected for {coin_pair}.")
            
    # return 1 if no pairs were found
    print("No coin pair found at this moment.")        
    return 1
    