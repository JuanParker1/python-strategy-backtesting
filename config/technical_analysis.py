"""
Indicators and price history tools for trading

@author: alexmnotfound
credits: gauss314
"""
import pandas as pd
import pandas_ta as ta
from datetime import datetime


#############################################
#########       Price history       #########
#############################################

def getHistoricoYFinance(symbol, start='2000-01-01', interval='1d', end=None):
    """
    Descarga de histórico de precios de Yahoo Finance

    :param symbol: Ticker a descargar
    :param start: Fecha de inicio (enero del 2000 por defecto)
    :param interval: Timeframe
    :param end: Fecha de fin
    :return:
    """
    import yfinance as yf

    data = yf.download(symbol, start=start, end=end, interval=interval, auto_adjust=True)

    return data


def binanceHistoricData(symbol, interval='1d', startTime=None, endTime=None, limit=1000):
    """
        Getting historic Data from Binance API
    :param symbol: ticker (BTCUSDT, ETHUSDT, etc..)
    :param interval:
        Minutes: 1m, 2m, 3m, 15m, 30m
        Hours: 1h, 2h, 4h
        Days: 1d, 3d
        Month: 1M
    :param startTime: time in ms
    :param endTime: time in ms
    :param limit: row limits (1000 default)
    :return: DataFrame with OHLC price history
    """
    import requests

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
    df = df.drop(['trades', 'qVolume'], axis=1)

    return df


def binanceHistoricDataFull(ticker, interval, dateFrom, dateTo):
    hist = binanceHistoricData(ticker,
                               interval=interval,
                               startTime=f'{dateToMs(dateFrom)}',
                               endTime=f'{dateToMs(dateTo)}')

    # Adjunto valores al DataFrame
    df = hist

    # Chequeo si el último row corresponde a la fecha final
    lastValue = dateToMs(hist.index[-1])

    while lastValue < dateToMs(dateTo):
        hist = binanceHistoricData(ticker,
                                   interval=interval,
                                   startTime=f'{lastValue}',
                                   endTime=f'{dateToMs(dateTo)}')

        lastValue = dateToMs(hist.index[-1])

        if lastValue == dateToMs(df.index[-1]):
            break

        df = df.append(hist)

    # Borro duplicados
    df.drop_duplicates(inplace=True)

    return df


def getDataExcel(ticker, timeframe):
    '''
    Busca excel de datos y devuelve DF
    '''
    import pandas as pd
    try:
        data = pd.read_excel(ticker + timeframe + '.xlsx').set_index('openTime').sort_index()
        # data.columns = ['Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume']
        data['pctChange'] = data.Close.pct_change()
    except:
        try:
            data = pd.read_excel('excels_csvs/ADRs/' + ticker + '.xlsx').set_index('timestamp').sort_index()
            data.columns = ['Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume']
            data['pctChange'] = data.AdjClose.pct_change()
        except:
            data = 'Sorry man no encontre el archivo en tus directorios'
    return data


def getDBData(ticker, interval, asset):
    '''
    path = os.getcwd() + '\\config\\csv\\'
    fileName = f'{ticker}-{interval}.csv'
    data = pd.read_csv(path + fileName)

    data.set_index('openTime', inplace=True)
    '''
    from config import db_management as query

    data = query.select(ticker=ticker, interval=interval, asset=asset)
    data.index = pd.to_datetime(data.index, utc=False)

    return data


#############################################
#########          Others           #########
#############################################

def dateToMs(date, utc=(-3)):
    """
    Cambia fecha a MS
    :param date: str(AAAA-MM-DD)
    :param utc: time zone
    :return: ms
    """
    try:
        dt_obj = datetime.strptime(f'{date} 00:00:00',
                                   '%Y-%m-%d %H:%M:%S')
    except:
        try:
            dt_obj = datetime.strptime(f'{date}',
                                       '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"No se pudo convertir la fecha: {e}")

    millisec = int(dt_obj.timestamp() * 1000) + (3600000 * utc)

    return millisec


def convert_datetime(dt):
    return datetime.strftime(dt, '%Y-%m-%d %H:%M-%S')


#############################################
#########        Indicators         #########
#############################################

def addPivots(df):
    '''
    Calculo los puntos pivote en base a un Dataframe.
    Los nombres de las columnas del DF deben estar en inglés (Open, High, Low, Close)

    '''
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

    '''
     PP = (HIGHprev + LOWprev + CLOSEprev) / 3    
     R1 = PP * 2 - LOWprev    
     S1 = PP * 2 - HIGHprev    
     R2 = PP + (HIGHprev - LOWprev)    
     S2 = PP - (HIGHprev - LOWprev)    
     R3 = PP * 2 + (HIGHprev - 2 * LOWprev)    
     S3 = PP * 2 - (2 * HIGHprev - LOWprev)    
     R4 = PP * 3 + (HIGHprev - 3 * LOWprev)    
     S4 = PP * 3 - (3 * HIGHprev - LOWprev)  
     R5 = PP * 4 + (HIGHprev - 4 * LOWprev)    
     S5 = PP * 4 - (4 * HIGHprev - LOWprev)
    '''
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


def analizarDivergencias(data):
    divergencias_alcistas = data.loc[(data.rsi_div.shift() < 0) & (data.rsi_pend.shift() > 0) & (data.rsi.shift() < 35)]
    divergencias_bajistas = data.loc[(data.rsi_div.shift() < 0) & (data.rsi_pend.shift() < 0) & (data.rsi.shift() > 65)]
    div = {}
    div['alcista_media'] = divergencias_alcistas.pctChange.mean() * 100
    div['alcista_q'] = divergencias_alcistas.pctChange.count()
    div['bajista_media'] = divergencias_bajistas.pctChange.mean() * 100
    div['bajista_q'] = divergencias_bajistas.pctChange.count()
    div['q'] = div['alcista_q'] + div['bajista_q']
    div['sesgo'] = div['alcista_media'] - div['bajista_media']
    return div


def addMACD(data, slow=26, fast=12, suavizado=9):
    df = data.copy()
    df['ema_fast'] = df.Close.ewm(span=fast).mean()
    df['ema_slow'] = df.Close.ewm(span=slow).mean()
    data['macd'] = df.ema_fast - df.ema_slow
    data['signal'] = data.macd.ewm(span=suavizado).mean()
    data['histograma'] = data.macd - data.signal
    data = data.dropna().round(2)
    return data


def addBollinger(data, ruedas=20, desvios=2):
    data['sma_20'] = data.AdjClose.rolling(20).mean()
    volatilidad = data.AdjClose.rolling(20).std()
    data['boll_inf'] = data.sma_20 - 2 * volatilidad
    data['boll_sup'] = data.sma_20 + 2 * volatilidad
    data.dropna(inplace=True)
    return data


def addSMA(data, n):
    data['sma_' + str(n)] = data.Close.rolling(n).mean()
    return data


def addEMA(data, n):
    data['ema_' + str(n)] = data.Close.ewm(span=n).mean()
    return data


def addFW(data, n):
    data['fw_' + str(n)] = (data.Close.shift(-n) / data.AdjClose - 1) * 100
    return data


def addAtr(data, period, maType):
    #
    ## True range calculation
    #
    import numpy as np

    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)

    if maType == 'sma':
        # SMA smoothing
        data['atr'] = true_range.rolling(period).mean()
    if maType == 'ema':
        data['atr'] = true_range.ewm(span=period).mean()
    if maType == 'rma':
        data['atr'] = ta.rma(true_range, period)

    return data


def addMaByType(data, column, maType, length):
    if maType == 'sma':
        # SMA smoothing:
        data[maType] = data[column].rolling(length).mean()
    if maType == 'ema':
        #   data[maType] = data[column].ewm(span=length).mean()
        data[maType] = ta.ema(data[column], length)
    if maType == 'rma':
        data[maType] = ta.rma(data[column], length)
    else:
        data[maType] = data[column].ewm(span=length).mean()

    return data


def addVolume(data):
    data['Volume'] = data.Volume / 1000000
    data['VolumeMA'] = data['Volume'].rolling(20).mean()

    return data


def addSource(data, source):
    if source == 'hl2':
        data['hl2'] = (data['High'] + data['Low']) / 2
    return data


def addPsar(df):
    """
    Devuelve Parabolic SAR con los valores de Trading View

    Librería necesaria:
        pip install -U git+https://github.com/twopirllc/pandas-ta

    :param df: DataFrame con columna "Close"
    :return: DataFrame con nueva columna "PSAR"
    """
    import numpy as np

    df.ta.psar(append=True)

    dfAux = df[['PSARl_0.02_0.2', 'PSARs_0.02_0.2']]

    df['PSAR'] = np.where(dfAux['PSARl_0.02_0.2'].isnull(), dfAux.index.map(dfAux['PSARs_0.02_0.2']),
                          dfAux['PSARl_0.02_0.2'])
    df = df.drop(['PSARl_0.02_0.2', 'PSARs_0.02_0.2', 'PSARaf_0.02_0.2', 'PSARr_0.02_0.2'], axis=1)

    return df
