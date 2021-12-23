import pandas as pd
import config.tickers as tk
import os
import matplotlib.pyplot as plt

tickers = ['RVNUSDT', 'AAVEUSDT']
tickers = tk.theBest
interval = '1h'
path = '/\\'


file1 = 'Detailed Results.csv'
df1 = pd.read_csv(path+file1)
df1.set_index('openTime', inplace=True)

dfVolume = pd.DataFrame()

for ticker in tickers:

    file2 = f'config\\csv\\{ticker}-{interval}.csv'
    df2 = pd.read_csv(path+file2)
    df2['Ticker'] = ticker
    df2['Volume'] = df2.Volume / 1000000
    df2['VolumeMA'] = df2['Volume'].rolling(20).mean()
    df2.set_index('openTime', inplace=True)

    dfVolume = pd.concat([dfVolume, df2[['Ticker', 'Volume', 'VolumeMA']]])


dfFinal = pd.merge(df1, dfVolume, how='left', on=['openTime', 'Ticker'])
print(dfFinal)

dfFinal.to_csv('DataConVolumen.csv')
