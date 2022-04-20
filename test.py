import requests
import numpy as np
import pandas as pd
from datetime import datetime
import config.technical_analysis as ta
from strategies import pmax
from analisis import newReporting as show
from config import info_tickers as tk

pd.options.display.max_columns = 10


def main():
    ############## INIT PMAX strategy parameters
    atrPeriod = 10
    atrMultiplierFrom = 8.0
    atrMultiplierTo = 9.0
    source = 'hl2'
    atrMa = 'sma'
    maType = 'rma'
    maLength = 10
    ############## END PMAX strategy parameters

    # script parameters
    asset = 'crypto'

    tickers = tk.quantCrypto
    tickers = ['BTCUSDT']

    intervals = ['1h']

    fromDate = ('2022-01-01')
    toDate = ('2022-04-19')

    backtestDf = pd.DataFrame()

    # PRINTING
    xlsWriter = True

    try:
        for ticker in tickers:
            for interval in intervals:
                # Create DataFrame
                print(f'Searching history for {ticker} in {interval}')
                df = getTickerData(ticker, interval, asset, fromDate, toDate, True)

                # Iter atr multipliers
                for i in np.arange(atrMultiplierFrom, atrMultiplierTo):
                    atrMultiplier = round(i, 2)
                    print(f'Calculating with atr multiplier of {atrMultiplier}')

                    # Executing Strategy
                    resultsList = pmax.applyPmaxFixedSl(df, atrMultiplier, maType, source, atrPeriod, atrMa, maLength)

                    # Turning results into DF and adding index
                    resultsDf = pd.DataFrame(resultsList)
                    resultsDf['openTime'] = df.index
                    resultsDf.set_index('openTime', inplace=True)
                    resultsDf = resultsDf.round(2)

                    # Saving trades into excel
                    resultsDf.to_excel('backtesting_trades.xlsx')
                    # print(resultsDf.sort_index(ascending=False).head(10))

                    # Dropping unnecesary columns
                    resultsDf.drop(['High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)

                    # Execute reports
                    reportDf = show.reporting(data=resultsDf)
                    reportDf['ticker'] = ticker
                    reportDf['atrMultiplier'] = atrMultiplier
                    reportDf['maType'] = maType
                    reportDf['maLen'] = maLength
                    reportDf['interval'] = interval
                    reportDf.set_index('ticker', inplace=True)

                    # Add to final df
                    backtestDf = backtestDf.append(reportDf)

    except Exception as e:
        print(f'ERROR: Process failed, {e}')

    # If printing to excel
    if xlsWriter:
        writer = pd.ExcelWriter('backtesting.xlsx', engine='xlsxwriter')
        df = backtestDf

        for i in df['atrMultiplier'].unique():
            df.loc[df['atrMultiplier'] == i].to_excel(writer, sheet_name=f'ATR {i}')

        dfGroup = df
        groupCols = ['maLen', 'interval', 'maType', 'atrMultiplier']
        dfGroup.reset_index(inplace=True)
        dfGroup.drop(['ticker'], axis=1, inplace=True)

        dfGroup = dfGroup.groupby(groupCols).sum()

        dfGroup['Biggest Win'] = df.groupby(groupCols)['Biggest Win'].max()
        dfGroup['Biggest Loss'] = df.groupby(groupCols)['Biggest Loss'].min()
        dfGroup['Efficiency'] = round(dfGroup['Trades Wins'] / (dfGroup['Longs Qty'] + dfGroup['Shorts Qty']) * 100, 2)

        dfGroup.to_excel(writer, sheet_name=f'General')

        print(dfGroup)

        writer.save()


def getTickerData(ticker, interval, asset, fromDate, toDate, db=True):
    """
    Gets ticker data depending on parameters
    """
    try:
        if db:
            data = ta.getDBData(ticker=ticker, interval=interval, asset=asset)

        else:
            data = ta.binanceHistoricDataFull(ticker=ticker, interval=interval, fromDate=fromDate, toDate=toDate)

        data['Ticker'] = ticker
        return data

    except Exception as e:
        print(f'ERROR: getTickerData failed, {e}')


if __name__ == main():
    main()
