"""
Armado de DataFrame y exportación a CSV de histórico de precios en Binance para distintos intervalos

@author: alexmnotfound
credits to: gauss314
"""
import sys
sys.path.append('/home/admin/PycharmProjects/python-strategy-backtesting')

import config.technical_analysis as ta
import config.info_tickers as tk
import os


def main():
    tickers = ['BTCUSDT', 'ADAUSDT', 'XTZUSDT', 'SOLUSDT', 'UNIUSDT',
               'LINKUSDT', 'ETHUSDT', 'DOTUSDT', 'XRPUSDT', 'EOSUSDT',
               'LTCUSDT', 'DOGEUSDT', 'MATICUSDT', 'AXSUSDT', 'BNBUSDT']
    # import config.tickers as tk
    tickers = tk.tickers
    # tickers = ['MANAUSDT', 'ENJUSDT']
    intervals = ['1d', '1w', '4h', '1h', '15m']

    fromDate = '2021-01-01'
    toDate = '2022-01-01'

    for ticker in tickers:
        for interval in intervals:
            # Creo DataFrame
            print(f'Descargando historial de {ticker} en {interval}')

            df = ta.binanceHistoricDataFull(ticker, interval, fromDate, toDate)

            df['Volume'] = df.Volume / 1000000
            df['VolumeMA'] = df['Volume'].rolling(20).mean()

            # Creo csv
            path = os.getcwd() + '/csv/'
            fileName = f'{ticker}-{interval}.csv'
            df.to_csv(path + fileName)

            print(f"{fileName} creado en {path}")
    print("Programa finalizado")


if __name__ == '__main__':
    main()
