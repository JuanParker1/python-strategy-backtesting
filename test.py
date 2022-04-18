import requests
import numpy as np
import pandas as pd
from datetime import datetime
import config.technical_analysis as ta
from strategies import pmax
from analisis import newReporting as show

pd.options.display.max_columns = 10


def main():
    # indicator parameters
    atrPeriod = 10
    atrMultiplierFrom = 13.0
    atrMultiplierTo = 16.0
    source = 'hl2'
    atrMa = 'sma'
    maType = 'rma'
    maLength = 10

    # script parameters
    tickers = ['BTCUSDT']
    intervals = ['1h']

    fromDate = ('2021-01-01')
    toDate = ('2021-12-30')

    backtestDf = pd.DataFrame()

    for ticker in tickers:
        for interval in intervals:
            # Create DataFrame
            print(f'Searching history for {ticker} in {interval}')
            df = ta.binanceHistoricDataFull(ticker, interval, fromDate, toDate)

            print(f'Adding indicators')
            df = ta.addSource(df, source)
            df = ta.addAtr(df, atrPeriod, atrMa)
            df = ta.addMaByType(df, source, maType, maLength)

            for i in np.arange(atrMultiplierFrom, atrMultiplierTo):
                atrMultiplier = round(i, 2)
                print(f'Calculating with atr multiplier of {atrMultiplier}')

                resultsList = pmax.applyStrategy(df, atrMultiplier, maType)

                resultsDf = pd.DataFrame(resultsList)
                resultsDf['openTime'] = df.index
                resultsDf.set_index('openTime', inplace=True)
                resultsDf = resultsDf.round(2)

                resultsDf.to_excel('backtesting_trades.xlsx')
                # print(resultsDf.sort_index(ascending=False).head(10))

                resultsDf.drop(['High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)

                # Execute reports
                reportDf = show.reporting(data=resultsDf)
                reportDf['ticker'] = ticker
                reportDf['atrMultipler'] = atrMultiplier
                reportDf['maType'] = maType
                reportDf['maLen'] = maLength
                reportDf['interval'] = interval
                reportDf.set_index('ticker', inplace=True)

                # Add to final df
                backtestDf = backtestDf.append(reportDf)

    backtestDf.to_excel('backtesting_resume.xlsx')


if __name__ == main():
    main()
