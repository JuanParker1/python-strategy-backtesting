import pandas as pd
import yfinance as yf

interval = '1d'
tasaLibreRiesgo = 0.01 / 360

dataBench = yf.download(tickers='spx', interval=interval, start='2020-01-01')


print(dataBench)