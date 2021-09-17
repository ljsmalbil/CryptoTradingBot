from binance import Client

api_key = # INSERT HERE
api_secret = # INSERT HERE

client = Client(api_key, api_secret)

float(client.get_asset_balance(asset='USDT')["free"])