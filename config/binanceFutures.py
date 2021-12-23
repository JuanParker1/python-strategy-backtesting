from binance.client import Client
from auth import binance_api, binance_secret

user_key = binance_api
secret_key = binance_secret
binance_client = Client(user_key, secret_key)

print(binance_client.futures_symbol_ticker(symbol='ALICEUSDT'))
