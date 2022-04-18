import pandas as pd
import numpy as np
import config.technical_analysis as ta


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
                ###################
                # Opening Longs
                ###################

                if np.isclose(value, row['Close'], rtol=pivotTolerance):
                    pivot_value = value

                    cond1 = row['smaFast'] >= row['smaSlow']
                    cond1 = cond1 & (row['Close']>=pivot_value)
                    cond2 = row['rsi'] >= rsi_long
                    cond3 = (abs((float(pivot_value) - float(row['PSAR'])) / float(pivot_value)) < 0.1)
                    #cond3 = row['Volume'] > row['VolumeMA']

                    if cond1 & trade_longs:
                        signal_obs = 'Go Long'
                        signal_status = 'Long'

                        signal_PE = row['Close']

                        if row['PSAR'] <= row['Close']:
                            if abs((float(pivot_value) - float(row['PSAR'])) / float(pivot_value)) > 0.1:
                                signal_SL = pivot_value * (1-max_lost)
                            else:
                                signal_SL = row['PSAR']
                        else:
                            signal_SL = pivot_value * (1-max_lost)

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


def estrategiaPivotsOriginal(dictValues, pivotTolerance):
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



def pivotsCalculation(df):
    '''
    Calculate Pivot Points from price DataFrame with OHLC.

    :param df: DataFrame with OHLC (Open, High, Low, Close)
    :return:
    '''
    try:
        # add pivots
        df = ta.addPivots(df)

        # Dropping unused columns and NAN values
        pivotes = df.drop(['Open', 'High', 'Low', 'Close'], axis=1).reset_index()
        pivotes['openTime'] = pivotes['openTime'].apply(ta.convert_datetime)
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
            pivotesData = ta.historicData(symbol=ticker, interval=interval)

        else:
            import yfinance as yf
            #  1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo and 3mo

            if interval == '1w':
                interval = '1wk'
            if interval == '1M':
                interval = '1mo'

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


def createTestingDf(tickers, interval, pivotes, smaSlow, smaFast, asset, testingMode):
    dfFinal = dict()
    i = 1
    for ticker in tickers:
        print(f"Creating testing DB for {ticker} ({i}/{len(tickers)})")
        i += 1
        # Is testing mode is on, searchs for CSV in folder
        if testingMode == 'On':
            data = ta.getDBData(ticker=ticker, interval=interval, asset=asset)

        else:
            # Getting candles price history of last 1000 sessions
            data = ta.historicData(symbol=ticker, interval=interval)
        data['Ticker'] = ticker

        # Adding sma & SAR
        data['smaSlow'] = data.Close.rolling(smaSlow).mean()
        data['smaFast'] = data.Close.rolling(smaFast).mean()
        data = ta.addRSI(data=data, ruedas=14)
        data = ta.addPsar(data)

        if asset == 'equity':
            from datetime import timedelta
            pivotes[ticker].index = pivotes[ticker].index + timedelta(hours=5)

        # Merging DF
        dfFinal[ticker] = pd.merge(data, pivotes[ticker], how='left', on='openTime')
        dfFinal[ticker].fillna(method='ffill', inplace=True)

        # Creating Sample df and adding signal columns with values
        dfFinal[ticker].index = pd.to_datetime(dfFinal[ticker].index)

    return dfFinal