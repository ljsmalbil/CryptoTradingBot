from binance import Client
from time_sync import Binance
#https://docs.python.org/3/faq/programming.html

api_key = # INSERT HERE
api_secret = # INSERT HERE

client = Client(api_key, api_secret)

recvWindow=60000

# rest in minutes
sell_rest = 15
buy_rest = 3

ROI = 1.005
USDT_amount = 50