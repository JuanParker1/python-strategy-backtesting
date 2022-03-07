"""
TODO: change pivots to db
TODO: convert equity and crypto str to var
TODO: check dates handling (utc, utc-3)
"""
import requests
import time
import pandas as pd
import numpy as np
from tqdm import tqdm
import config.info_weeks as wk
import os
from config import info_tickers as tk
from datetime import datetime
import database_mangmnt as query

from config.conn_telegram import sendMsg

testingMode = 'On'

pd.options.mode.chained_assignment = None  # default='warn'


def main():
    # Setting Parameters
    isEquity = 'equity'
    isCrypto = 'crypto'
    asset = isEquity
    pivotInterval = '1w'
    pivotTolerance = 0.015
    candlesInterval = '1h'
    smaValue = 7
    resultsList = list()
    weeks = wk.weeks

    # Weeks & tickers to check
    if asset == 'equity':
        # tickers = tk.cedears
        tickers = ['AAPL', 'TSLA']
    else:
        tickers = tk.tickers

    # Pivot calculation
    pivotes = downloadPivotes(tickers=tickers, interval=pivotInterval, type=asset)

    # Creating initial DB to work with
    dataInit = createTestingDf(tickers=tickers,
                               interval=candlesInterval,
                               pivotes=pivotes,
                               smaValue=smaValue,
                               asset=asset)
    # Backtesting
    for week in weeks:
        dateFromSample = week[0]
        dateToSample = week[1]

        # Pivot calculation
        print(f'\nCalculating week {week[0]} to {week[1]}')

        for ticker in tickers:

            # Sampling Dumpling
            cond1 = (dataInit[ticker].index >= dateFromSample)
            cond2 = (dataInit[ticker].index <= dateToSample)
            mask = cond1 & cond2

            data = addColumns(dataInit[ticker].loc[mask])
            data = data.fillna(0)
            data.reset_index(inplace=True)
            data['Week'] = week[0]

            # Converting DataFrame to Dict
            dataDict = data.to_dict('records')

            if len(dataDict) > 0:
                ################
                # Apply strategy
                ################
                dataWithTrades = estrategiaPivots(dictValues=dataDict,
                                                  pivotTolerance=pivotTolerance)

                resultsList.append(dataWithTrades)

            else:
                print(f'No se encontraron resultados para {ticker}')

    print("\nConvirtiendo listas a DF")
    time.sleep(1)
    listToDf = list()

    for lista in tqdm(resultsList):
        listToDf.extend(lista)

    resultsDf = pd.DataFrame(listToDf)

    print("\nConvirtiendo resultados a CSV")
    resultsDf.to_csv('resultsEqty.csv')
    #resultsDf.to_excel('testing Results.b xlsx')
    print('Results.CSV created')

    print(f'\nReporting')
    reportingView(df=resultsDf)
    #reporting(interval=pivotInterval, type=asset)

    try:
        reporting(interval=pivotInterval, type=asset)
    except Exception as e:
        print(f'Nope> {e}')


def convert_datetime(dt):
    return datetime.strftime(dt, '%Y-%m-%d %H:%M-%S')


def historicData(symbol, interval='1d', startTime=None, endTime=None, limit=1000):
    """
        Getting historic Data from Binance API

    :param symbol: ticker (BTCUSDT, ETHUSDT, etc..)
    :param candlesInterval:
        Minutes: 1m, 2m, 3m, 15m, 30m
        Hours: 1h, 2h, 4h
        Days: 1d, 3d
        Month: 1M
    :param startTime:
    :param endTime:
    :param limit:
    :return: DataFrame with OHLC price history
    """

    url = 'https://api.binance.com/api/v3/klines'

    params = {'symbol': symbol, 'interval': interval,
              'startTime': startTime, 'endTime': endTime, 'limit': limit}

    r = requests.get(url, params=params)
    js = r.json()

    # Creating Dataframe
    cols = ['openTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'cTime',
            'qVolume', 'trades', 'takerBase', 'takerQuote', 'Ignore']

    df = pd.DataFrame(js, columns=cols)

    # Converting strings to numeric
    df = df.apply(pd.to_numeric)

    # Timestamp Index handling
    df.index = pd.to_datetime(df.openTime, unit='ms')

    # Dropping unused columns
    df = df.drop(['openTime', 'cTime', 'takerBase', 'takerQuote', 'Ignore'], axis=1)
    df = df.drop(['Volume', 'qVolume', 'trades'], axis=1)

    return df


def pivotsCalculation(df):
    '''
    Calculate Pivot Points from price DataFrame with OHLC.

    :param df: DataFrame with OHLC (Open, High, Low, Close)
    :return:
    '''
    try:
        df['PP'] = (df.High.shift(1) + df.Low.shift(1) + df.Close.shift(1)) / 3
        df['R1'] = (2 * df.PP) - df.Low.shift(1)
        df['R2'] = df.PP + (df.High.shift(1) - df.Low.shift(1))
        df['R3'] = df.High.shift(1) + (2 * (df.PP - df.Low.shift(1)))
        df['R4'] = df.PP * 3 + (df.High.shift(1) - 3 * df.Low.shift(1))
        df['R5'] = df.PP * 4 + (df.High.shift(1) - 4 * df.Low.shift(1))
        df['S1'] = (2 * df.PP) - df.High.shift(1)
        df['S2'] = df.PP - (df.High.shift(1) - df.Low.shift(1))
        df['S3'] = df.Low.shift(1) - (2 * (df.High.shift(1) - df.PP))
        df['S4'] = df.PP * 3 - (3 * df.High.shift(1) - df.Low.shift(1))
        df['S5'] = df.PP * 4 - (4 * df.High.shift(1) - df.Low.shift(1))

        # Dropping unused columns and NAN values
        pivotes = df.drop(['Open', 'High', 'Low', 'Close'], axis=1).reset_index()
        pivotes['openTime'] = pivotes['openTime'].apply(convert_datetime)
        pivotes['openTime'] = pd.to_datetime(pivotes.openTime).dt.tz_localize(None)
        pivotes.set_index('openTime', inplace=True)
        pivotes.index = pd.to_datetime(pivotes.index, utc=False)
        pivotes.dropna(inplace=True)

        return pivotes

    except Exception as e:
        print(f'Dataframe can not be processed: {e}')


def downloadPivotes(tickers, interval, type):
    pivotes = dict()
    i = 1

    for ticker in tickers:
        if type == 'Crypto':

            print(f"Downloading & calculating pivots for {ticker} ({i}/{len(tickers)})")
            i += 1
            # Getting pivotes price history of last 1000 sessions
            pivotesData = historicData(symbol=ticker, interval=interval)

        else:
            import yfinance as yf
            if interval == '1w':
                interval = '1wk'

            pivotesData = yf.download(tickers=ticker, interval=interval)
            pivotesData.index.rename('openTime', inplace=True)
            pivotesData.index = pivotesData.index + pd.DateOffset(hours=9.5)
            # Converting strings to numeric
            pivotesData = pivotesData.apply(pd.to_numeric)

            # Timestamp Index handling
            pivotesData.index = pd.to_datetime(pivotesData.index, unit='ms')

        pivotes[ticker] = pivotsCalculation(pivotesData)

    return pivotes


def addColumns(data):
    data['Variacion'] = data['Close'].pct_change() * 100

    # create signals
    data['Signal'] = 'None'
    data['VarPos'] = 0.00
    data['VarMin'] = 0.00
    data['VarMax'] = 0.00
    data['PE'] = 0.00
    data['TP'] = 0.00
    data['SL'] = 0.00
    data['Result'] = 0.00
    data['Obs'] = ''

    return data


def addPsar(df):
    """
    Devuelve Parabolic SAR con los valores de Trading View

    Librería necesaria:
        pip install -U git+https://github.com/twopirllc/pandas-ta

    :param df: DataFrame con columna "Close"
    :return: DataFrame con nueva columna "PSAR"
    """
    from pandas_ta import psar

    df.ta.psar(append=True)

    dfAux = df[['PSARl_0.02_0.2', 'PSARs_0.02_0.2']]

    df['PSAR'] = np.where(dfAux['PSARl_0.02_0.2'].isnull(), dfAux.index.map(dfAux['PSARs_0.02_0.2']), dfAux['PSARl_0.02_0.2'])
    df = df.drop(['PSARl_0.02_0.2', 'PSARs_0.02_0.2', 'PSARaf_0.02_0.2', 'PSARr_0.02_0.2'], axis=1)

    return df


def addRSI(data, ruedas, ruedas_pend=1):
    """
    Agrega la columna RSI a nuestro dataframe, basado en su columna Close

    :param data: DataFrame con columna Close
    :param ruedas: integer, La cantidad de ruedas para el cálculo del RSI
    :param ruedas_pend: integer, opcional (Cantidad de ruedas para calcular pendiente del RSI y su divergencia)
    :return: DataFrame con RSI
    """
    import numpy as np
    df = data.copy()
    df['dif'] = df.Close.diff()
    df['win'] = np.where(df['dif'] > 0, df['dif'], 0)
    df['loss'] = np.where(df['dif'] < 0, abs(df['dif']), 0)
    df['ema_win'] = df.win.ewm(alpha=1 / ruedas).mean()
    df['ema_loss'] = df.loss.ewm(alpha=1 / ruedas).mean()
    df['rs'] = df.ema_win / df.ema_loss
    data['rsi'] = 100 - (100 / (1 + df.rs))

    if ruedas_pend != 0:
        data['rsi_pend'] = (data.rsi / data.rsi.shift(ruedas_pend) - 1) * 100
        precio_pend = (data.Close / data.Close.shift(ruedas_pend) - 1) * 100
        data['rsi_div'] = data.rsi_pend * precio_pend
    return data


def getDBData(ticker, interval, asset):
    '''
    path = os.getcwd() + '\\config\\csv\\'
    fileName = f'{ticker}-{interval}.csv'
    data = pd.read_csv(path + fileName)

    data.set_index('openTime', inplace=True)
    '''
    data = query.select(ticker=ticker, interval=interval, asset=asset)
    data.index = pd.to_datetime(data.index, utc=False)

    return data


def createTestingDf(tickers, interval, pivotes, smaValue, asset):
    dfFinal = dict()
    i = 1
    for ticker in tickers:
        print(f"Creating testing DB for {ticker} ({i}/{len(tickers)})")
        i += 1
        # Is testing mode is on, searchs for CSV in folder
        if testingMode == 'On':
            data = getDBData(ticker=ticker, interval=interval, asset=asset)

        else:
            # Getting candles price history of last 1000 sessions
            data = historicData(symbol=ticker, interval=interval)
        data['Ticker'] = ticker


        # Adding sma & SAR
        data['sma'] = data.Close.rolling(smaValue).mean()
        data = addRSI(data=data, ruedas=14)
        data = addPsar(data)

        if asset == 'equity':
            from datetime import timedelta
            pivotes[ticker].index = pivotes[ticker].index + timedelta(hours=5)

        # Merging DF
        dfFinal[ticker] = pd.merge(data, pivotes[ticker], how='left', on='openTime')
        dfFinal[ticker].fillna(method='ffill', inplace=True)

        # Creating Sample df and adding signal columns with values
        dfFinal[ticker].index = pd.to_datetime(dfFinal[ticker].index)

    return dfFinal


def estrategiaPivots(dictValues, pivotTolerance):
    # Setting parameters for iteration
    values_list = list()
    prevSignal = signal_status = 'None'
    signal_PE = 0
    signal_SL = 0
    signal_obs = ''

    trade_shorts = False
    trade_longs = True
    rsi_long = rsi_short = 40
    max_lost = 0.1

    for row in dictValues:
        array = (row['S5'], row['S4'], row['S3'], row['S2'], row['S1'], row['PP'],
                 row['R1'], row['R2'], row['R3'], row['R4'], row['R5'])

        ######################################
        # Handling None signals (initial rows)
        ######################################
        if prevSignal == 'None':
            for value in array:
                if np.isclose(value, row['Close'], rtol=pivotTolerance):
                    signal_status = 'First_flag'
                    pivot_value = value
                    signal_obs = 'Price near to Pivot'

        ######################
        # Handling first flag
        ######################
        if prevSignal == 'First_flag':
            signal_status = 'Second_flag'

            if row['Close'] >= pivot_value:
                signal_obs = 'Long Approaching'
            else:
                signal_obs = 'Short Approaching'

        ######################
        # Handling second flag
        ######################
        if prevSignal == 'Second_flag':
            signal_status = 'First_flag'

            if np.isclose(pivot_value, row['Close'], rtol=pivotTolerance):
                ###################
                # Opening Longs
                ###################
                cond1 = row['Close'] >= pivot_value
                cond2 = row['rsi'] >= rsi_long
                cond3 = (abs((float(pivot_value) - float(row['PSAR'])) / float(pivot_value)) < 0.1)
                #cond3 = row['Volume'] > row['VolumeMA']

                if cond1 & cond2 & trade_longs:
                    signal_status = 'Long'
                    signal_PE = row['Close']

                    if row['PSAR'] <= row['Close']:
                        if abs((float(pivot_value) - float(row['PSAR'])) / float(pivot_value)) > 0.1:
                            signal_SL = pivot_value * (1-max_lost)
                        else:
                            signal_SL = row['PSAR']
                    else:
                        signal_SL = pivot_value * (1-max_lost)

                ###################
                # Opening Shorts
                ###################
                cond1 = row['Close'] <= pivot_value
                cond2 = row['rsi'] < rsi_short
                cond3 = (abs((float(row['PSAR']) - float(pivot_value)) / float(pivot_value)) < 0.1)
                #cond4 = row['Volume'] > row['VolumeMA']

                if cond1 & cond2 & trade_shorts:
                    signal_status = 'Short'
                    signal_PE = row['Close']

                    if row['PSAR'] >= row['Close']:
                        if abs((float(row['PSAR']) - float(pivot_value)) / float(pivot_value)) > 0.1:
                            signal_SL = pivot_value * (1+max_lost)
                        else:
                            signal_SL = row['PSAR']
                    else:
                        signal_SL = pivot_value * (1+max_lost)

            if signal_status == 'First_flag':
                signal_obs = f'Waiting for confirmation'
            else:
                signal_obs = f'{signal_status} Trade Active'

        ###################
        # Handling Longs
        ###################
        if prevSignal == 'Long':

            if signal_PE != 0:
                signal_obs = 'Hold'

                if row['Low'] <= signal_SL:
                    # Cierro posición si toca SL
                    row['Result'] = (signal_SL - signal_PE) / signal_PE * 100
                    signal_status = 'None'
                    signal_obs = 'Toca SL'
                    signal_PE = 0
                    signal_SL = 0

                elif row['PSAR'] > row['Close']:
                    SL = row['High'] * (1-max_lost)
                    if SL > signal_SL:
                        signal_SL = SL
                        signal_obs = 'Muevo SL'

                elif abs((float(signal_PE) - float(row['PSAR'])) / float(signal_PE)) > 0.1:
                    signal_SL = signal_PE * (1-max_lost)
                    signal_obs = 'Muevo SL'

                else:
                    signal_SL = row['PSAR']
                    signal_obs = 'Muevo SL'

        ###################
        # Handling Shorts
        ###################
        if prevSignal == 'Short':

            if signal_PE != 0:
                signal_obs = 'Hold'

                if row['High'] >= signal_SL:
                    # Cierro posición si toca SL
                    row['Result'] = (signal_PE - signal_SL) / signal_PE * 100
                    signal_status = 'None'
                    signal_obs = 'Toca SL'
                    signal_PE = 0
                    signal_SL = 0

                elif row['PSAR'] < row['Close']:
                    SL = row['Low'] * (1+max_lost)
                    if SL < signal_SL:
                        signal_SL = SL
                        signal_obs = 'Muevo SL'

                elif abs((float(row['PSAR']) - float(signal_PE)) / float(signal_PE)) > 0.1:
                    SL = row['Close'] * (1+max_lost)
                    if SL < signal_SL:
                        signal_SL = SL
                        signal_obs = 'Muevo SL'

                else:
                    signal_SL = row['PSAR']
                    signal_obs = 'Muevo SL'

        row['PE'] = signal_PE
        row['SL'] = signal_SL
        row['Signal'] = signal_status
        row['Obs'] = signal_obs

        prevSignal = signal_status

        values_list.append(row)

    # Cierro posiciones restantes
    try:
        if values_list[-1]['Obs'] in (['Long Trade Active', 'Short Trade Active', 'Muevo SL']):
            values_list[-1]['Obs'] = 'Cierro Pos'
            if values_list[-1]['Signal'] == 'Short':
                values_list[-1]['Result'] = (signal_PE - values_list[-1]['Close']) / signal_PE * 100
            else:
                values_list[-1]['Result'] = (values_list[-1]['Close'] - signal_PE) / signal_PE * 100
    except:
        False


    return values_list


def reportingView(df):
    longs = (df['Obs'] == 'Long Trade Active')
    shorts = (df['Obs'] == 'Short Trade Active')

    ##########################
    # DF with results by week
    ##########################
    resultsByWeek = pd.DataFrame()
    weeks = df['Week'].unique()

    for week in weeks:
        aux = df.loc[df['Week'] == week]
        aux = pd.DataFrame(data={'Result': sum(aux['Result']),
                                 'Longs': aux.loc[longs]['Obs'].count(),
                                 'Shorts': aux.loc[shorts]['Obs'].count(),
                                 'Biggest_Loss': aux['Result'].min(),
                                 'Biggest_Win': aux['Result'].max()},
                           index=[week])

        aux = aux.round(2)
        resultsByWeek = resultsByWeek.append(aux)

    ##########################
    # DF with results by coin
    ##########################
    resultsByCoin = pd.DataFrame()
    tickers = df['Ticker'].unique()

    for ticker in tickers:
        aux = df.loc[df['Ticker'] == ticker]
        aux = pd.DataFrame(data={'Result': sum(aux['Result']),
                                 'Longs': aux.loc[longs]['Obs'].count(),
                                 'Shorts': aux.loc[shorts]['Obs'].count(),
                                 'Biggest_Loss': aux['Result'].min(),
                                 'Biggest_Win': aux['Result'].max()},
                           index=[ticker])

        aux = aux.round(2)
        resultsByCoin = resultsByCoin.append(aux)

    print("\nResultados por semana")
    print(resultsByWeek)

    print("\nResultados por moneda")
    print(resultsByCoin)


def reporting(interval, type='Equity'):
    import pandas as pd
    import matplotlib.pyplot as plt
    import config.info_weeks as wk
    from datetime import datetime, timedelta

    import warnings
    import matplotlib.cbook

    warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

    weeks = wk.weeks

    file = 'resultsEqty.csv'
    data = pd.read_csv(file)

    ################
    #### SHARPE
    ################

    tasaLibreRiesgo = 0.01 / 360

    if type == 'crypto':
        bench = 'BTC'
        dataBench = pd.read_csv('C:\\Users\\Matias.MSI\\PycharmProjects\\backtesting\\config\\csv\\BTCUSDT-1w.csv')
        dataBench.set_index(['openTime'], inplace=True)

        dataBench.index = pd.to_datetime(dataBench.index)

    if type == 'equity':
        import yfinance as yf
        bench = 'SPY'
        if interval == '1w':
            interval = '1wk'

        dataBench = yf.download(tickers=bench, interval=interval)
        dataBench.index.rename('openTime', inplace=True)

        # Timestamp Index handling
        dataBench.index = pd.to_datetime(dataBench.index, unit='ms')


    dataBench['Var'] = dataBench['Close'].pct_change() * 10
    # Converting strings to numeric
    print(dataBench)
    dataBench = dataBench.apply(pd.to_numeric)

    rendBench = dataBench['Var'].sum()
    rendimientoBench = dataBench['Var'].mean()
    desvioBench = dataBench['Var'].std()
    sharpeBench = (rendimientoBench - tasaLibreRiesgo) / desvioBench

    rendimientos = data['Result'].mean()
    desvios = data['Result'].std()
    sharpe = (rendimientos - tasaLibreRiesgo) / desvios

    ################
    #### DATOS
    ################

    longsQty = (data['Obs'] == 'Long Trade Active')
    longsQty = data.loc[longsQty]['Obs'].count()

    shortsQty = (data['Obs'] == 'Short Trade Active')
    shortsQty = data.loc[shortsQty]['Obs'].count()

    tradesPos = (data['Result'] > 0)
    tradesPos = data.loc[tradesPos]['Obs'].count()

    longsPos = (data['Signal'] == 'Long')
    longsPos = data.loc[longsPos & tradesPos]['Obs'].count()

    tradesNeg = (data['Result'] < 0)
    tradesNeg = data.loc[tradesNeg]['Obs'].count()

    rendPromPos = (data['Result'] > 0)
    rendPromPos = data.loc[rendPromPos]['Result'].mean().round(2)

    rendPromNeg = (data['Result'] < 0)
    rendPromNeg = data.loc[rendPromNeg]['Result'].mean().round(2)

    fechaIni = data['openTime'].min()
    fechaIni = datetime.strptime(fechaIni, '%Y-%m-%d %H:%M:%S')
    fechaIni = datetime.date(fechaIni)

    fechaFin = data['openTime'].max()
    fechaFin = datetime.strptime(fechaFin, '%Y-%m-%d %H:%M:%S')
    fechaFin = datetime.date(fechaFin)

    weeksQty = (fechaFin - fechaIni).days // 7

    rendTot = (data['Result'] != 0)
    rendTot = data.loc[rendTot]['Result'].sum().round(2)

    #################################
    ### BEST AND WORSE
    #################################

    data = data.sort_values(by=['openTime'], ascending=False)

    ###### BEST  #########

    best10Pos = data[['Ticker', 'Result', 'Signal', 'PE', 'SL', 'openTime']].loc[data['Result'] > 0]
    best10Pos = best10Pos.sort_values(by=['Result'], ascending=False).head(10)

    for index, row in best10Pos.iterrows():
        cond1 = data['Ticker'] == row.Ticker
        cond2 = data['openTime'] < row.openTime

        best10Pos.at[index, ['Signal']] = data['Signal'].loc[cond1 & cond2].iloc[0]
        best10Pos.at[index, ['PE']] = data['PE'].loc[cond1 & cond2].iloc[0]
        best10Pos.at[index, ['SL']] = data['SL'].loc[cond1 & cond2].iloc[0]

    best10Pos.columns = ['Simbolo', 'Resultado', 'Trade', 'Apertura', 'Cierre', 'Fecha Cierre']
    best10Pos = best10Pos.round(4)
    best10Pos['Resultado'] = best10Pos['Resultado'].round(2)
    best10Pos.set_index('Simbolo', inplace=True)

    ###### WORST  #########

    worst10Pos = data[['Ticker', 'Result', 'Signal', 'PE', 'SL', 'openTime']].loc[data['Result'] < 0]
    worst10Pos = worst10Pos.sort_values(by=['Result'], ascending=True).head(10)

    for index, row in worst10Pos.iterrows():
        cond1 = data['Ticker'] == row.Ticker
        cond2 = data['openTime'] < row.openTime

        worst10Pos.at[index, ['Signal']] = data['Signal'].loc[cond1 & cond2].iloc[0]
        worst10Pos.at[index, ['PE']] = data['PE'].loc[cond1 & cond2].iloc[0]
        worst10Pos.at[index, ['SL']] = data['SL'].loc[cond1 & cond2].iloc[0]

    worst10Pos.columns = ['Simbolo', 'Resultado', 'Trade', 'Apertura', 'Cierre', 'Fecha Cierre']
    worst10Pos = worst10Pos.round(4)
    worst10Pos['Resultado'] = worst10Pos['Resultado'].round(2)
    worst10Pos.set_index('Simbolo', inplace=True)

    #################################
    ### PRINTING GOES BRRRRRRRRRRRR
    #################################

    print("\n\n## Resultados ##")
    print(f"Periodo analizado: {fechaIni} a {fechaFin}")
    print(f"Cantidad semanas: {weeksQty}")
    print(f"Cantidad de trades: {longsQty + shortsQty}")
    print(f"Cantidad de longs: {longsQty}")
    print(f"Cantidad de shorts: {shortsQty}")
    print(f"Cantidad ganadores: {tradesPos}")
    print(f"Cantidad perdedores: {tradesNeg}")

    print("\n## Rendimientos ##")
    print(f"Rendimiento Total: {round(rendTot, 2)}%")
    print(f"Rendimiento promedio (semanal): {round(rendTot / weeksQty, 2)}%")
    print(f"Rendimiento promedio ganadores: {round(rendPromPos, 2)}")
    print(f"Rendimiento promedio perdedores: {round(rendPromNeg, 2)}")

    print(f"\n## Volatilidad (vs {bench}) ##")

    df = pd.DataFrame(data={f'{bench}': [f'{round(rendBench, 2)}%',
                                    f'{round(rendBench / weeksQty, 2)}%',
                                    f'{round(sharpeBench * 7, 6)}'],
                            'Estrategia': [f'{round(rendTot, 2)}%',
                                           f'{round(rendTot / weeksQty, 2)}%',
                                           f'{round(sharpe * 7, 6)}']},
                      index=['Rendimiento del periodo',
                             'Rendimiento promedio semanal',
                             'Sharpe Semanal'])
    dfCompare = df
    print(dfCompare)

    print("\n######### Mejores 10 Trades #########")
    print(best10Pos)

    print("\n######### Peores 10 Trades #########")
    print(worst10Pos)

    #################################
    ### Calculating Weekly things
    #################################

    weeklyResultsdf = list([[0, 0]])
    weeklyResultsBench = list([[0, 0]])

    for week in weeks:
        cond1 = data['openTime'] >= week[0]
        cond2 = data['openTime'] < week[1]
        cond3 = dataBench.index >= week[0]
        cond4 = dataBench.index < week[1]

        df = data.loc[cond1 & cond2]

        dfBench = dataBench.loc[cond3 & cond4]


        weeklyResultsdf.append([week[0], df['Result'].sum()])
        weeklyResultsBench.append([week[0], dfBench['Var'].sum()])

    weeklyResultsdf = pd.DataFrame(data=weeklyResultsdf)
    weeklyResultsdf.columns = ['Semana', 'Resultado']
    weeklyResultsdf['Acumulado'] = weeklyResultsdf['Resultado'].cumsum()
    weeklyResultsStrat = weeklyResultsdf[['Acumulado']]

    weeklyResultsBench = pd.DataFrame(data=weeklyResultsBench)
    weeklyResultsBench.columns = ['Semana', 'Resultado']
    weeklyResultsBench['Acumulado'] = weeklyResultsBench['Resultado'].cumsum()

    #################################
    ###  REPORTING PLOTING
    #################################

    fig, axs = plt.subplots(nrows=3, ncols=2)
    fig.tight_layout()

    # Variación Capital
    axs[0][0].plot(weeklyResultsStrat['Acumulado'])
    axs[0][0].set_xlabel('Semana')
    axs[0][0].set_title('Variación semanal del capital')

    weeklyResultsdf['Resultado'].plot(ax=axs[1][0], kind='bar', width=0.1, title='').set_xlabel('')

    # Variación Bench
    axs[0][1].plot(weeklyResultsBench['Acumulado'])
    axs[0][1].set_xlabel('Semana')
    axs[0][1].set_title(f'Variación semanal de {bench}')

    cond5 = weeklyResultsBench.index >= weeklyResultsBench.index[0]
    cond6 = weeklyResultsBench.index <= weeklyResultsBench.index[-1]
    weeklyResultsBench = weeklyResultsBench.loc[cond5 & cond6]
    weeklyResultsBench.reset_index(inplace=True)

    weeklyResultsBench['Resultado'].plot(ax=axs[1][1], kind='bar', width=0.1, title='').set_xlabel('')

    # Rendimiento comparado
    df = pd.DataFrame(data={f'{bench}': [round(rendBench, 2)],
                            'Estrategia': [round(rendTot, 2)]},
                      index=[''])

    df.plot(ax=axs[2][0], kind='bar', width=0.1, title='Rendimiento (%)').set_xlabel('Rendimiento')

    # Sharpe
    df = pd.DataFrame(data={f'{bench}': [round(sharpeBench * 7, 6)],
                            'Estrategia': [round(sharpe * 7, 6)]},
                      index=[''])

    df.plot(ax=axs[2][1], kind='bar', width=0.1, title='Sharpe Semanal').set_xlabel('Sharpe Ratio')

    plt.show()


if __name__ == '__main__':
    main()
