from binance import Client
import time
import config

class Orders():
    def __init__(self, coin_pair, price, amount):
        self.coin_pair = coin_pair
        self.price = price
        self.amount = amount
        
    def buy(self, qty):
        """This function carries out the purchase once a signal has been given.

        Parameters
        ----------
        self : self
            Self object variable.
        qty : float
            The quantity of tokens to be bought. 
        Returns
        ----------
        status : int
            Status code. 1 if purchase was successful, otherwise 0.
        """
        
        client = config.client
        rest = config.buy_rest
        
        # create buy order
        client.create_order(symbol=self.coin_pair, side="BUY", type="LIMIT", quantity=qty, timeInForce="GTC", price=self.price)

        # start clock
        current = time.time()

        time.sleep(1)

        # check if order is open
        
        while len(client.get_open_orders(symbol=self.coin_pair)) != 0:
            # cancel automated sell order after 'rest' minutes
            if (time.time() - current) > (rest * 60):
                open_order = client.get_open_orders(symbol=self.coin_pair)
                client.cancel_order(symbol=self.coin_pair, orderId=open_order[0]["orderId"])
                print("Buy order not executed. Order canceled.")
                return 1

        return 0
    
    def sell(self, qty, precision = 4):
        """This function carries out the purchase once a signal has been given.

        Parameters
        ----------
        self : self
            Self object variable.
        qty : float
            The quantity of tokens to be bought. 
        precision : int, default : 4
            Price precision. 

        Returns
        ----------
        status : int
            Status code. 1 if purchase was successful, otherwise 0.
        """
        client = config.client
        ROI = config.ROI
        rest = config.sell_rest
        
        #price = round(self.price * ROI, precision)

        # compute price to reach desired profit
        
        #output_amount = self.amount * ROI
        #sell_price = output_amount / qty
        
        sell_price = self.price * ROI
        sell_price = round(sell_price, precision)
        
        # create sell order
        client.create_order(symbol=self.coin_pair, side="SELL", type="LIMIT",
                            quantity= qty,
                            timeInForce="GTC", price=sell_price)

        # start clock
        current = time.time()

        # check if order is open
        while len(client.get_open_orders(symbol=self.coin_pair)) != 0:
            time.sleep(30)
            print("Sell order Open...")
            # stop running after 'rest' minutes and cancel order
            if (time.time() - current) > (rest * 60):
                open_order = client.get_open_orders(symbol=self.coin_pair)
                #client.cancel_order(symbol=self.coin_pair, orderId=open_order[0]["orderId"])
                
                return 1

        return 0

