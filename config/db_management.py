"""
TODO: date to excludes the indicated that. May be difficult to assimilate on the long run
TODO: AAPL (and gods know how many) doesn't remove duplicates when inserting
"""

import sys
sys.path.append('/')

from sqlalchemy import create_engine
import config.binance_tocsv as binance
import pandas as pd
import config.info_tickers as tk
import yfinance as yf


def main():
    # Setting parameters
    is_crypto, is_equity = 'crypto', 'equity'
    enviroment = is_equity
    intervals = ['1h']
    dateFrom = '2021-01-01'
    dateTo = '2022-01-01'

    if enviroment == is_equity:
        tickers = tk.cedears
        tickers = ['AAPL', 'TSLA']
    if enviroment == is_crypto:
        tickers = ['BTCUSDT', 'ETHUSDT']
        # tickers = tk.tickers

    # Setting DBConn USER : PASS @ HOST / BBDD_NAME
    engine = create_engine(f'mysql+pymysql://root:@localhost/{enviroment}')

    for ticker in tickers:
        for interval in intervals:

            if enviroment == is_crypto:
                df = binance.historicDataFull(ticker, interval, dateFrom, dateTo)
            if enviroment == is_equity:
                if interval == '1w':
                    interval = '1wk'
                df = yf.download(tickers=ticker, interval=interval, start=dateFrom, end=dateTo)

            df.index = pd.to_datetime(df.index,  format='%Y-%m-%d %H:%M')
            df.index = df.index.values.astype('datetime64[s]')
            df.index.rename('openTime', inplace=True)

            df['Volume'] = df.Volume / 1000000
            df['VolumeMA'] = df['Volume'].rolling(20).mean()
            df = df.fillna(0)

            # Define here what you want to do
            insert(engine=engine, ticker=ticker, interval=interval, data_insert=df)


def select(ticker, interval, year='2021', asset=''):
    # Setting DBConn USER : PASS @ HOST / BBDD_NAME
    engine = create_engine(f'mysql+pymysql://root:@localhost/{asset}')

    # Setting the symbol table_name to lowecase and defining table table_name
    ticker = ticker.lower()
    table_name = year + ticker + interval

    query = f'Select * From {table_name}'
    data = pd.read_sql(query, engine)
    data.set_index('openTime', inplace=True)
    data.sort_index(inplace=True)
    data = data.fillna(0)

    return data


def insert(engine, ticker, interval, data_insert, year='2021'):
    # Setting the symbol table_name to lowecase and defining table table_name
    ticker = ticker.lower()
    table_name = year + ticker + interval

    # Check if table exists
    try:
        print(f"{ticker}: descargando datos de DB")
        query = f'Select * From {table_name}'
        data = pd.read_sql(query, engine)
        data.set_index('openTime', inplace=True)
        data.sort_index(inplace=True)
        data = data.fillna(0)
    except Exception as e:
        data = pd.DataFrame()
        print(f"{ticker}: no se encontró la tabla {table_name}. Se creará con los datos descargados.")

    # Comparing Df's and inserting data in DB
    df = pd.concat([data, data_insert])
    df = df.reset_index(drop=False)
    df = df.round(4)
    df_gpby = df.groupby(list(df.columns))
    idx = [x[0] for x in df_gpby.groups.values() if len(x) == 1]

    data = df.reindex(idx)

    if len(data) > 0:
        data.set_index('openTime', inplace=True)
        data.to_sql(con=engine, name=f'{table_name}', if_exists='append', index_label=['openTime'])
        print(f"{ticker}: se insertaron correctamente los valores en {table_name}\n")
        return data
    else:
        print(f'{ticker}: No se encontraron valores para insertar\n')



if __name__ == '__main__':
    main()
