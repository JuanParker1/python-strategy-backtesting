"""
TODO: change pivots to db
TODO: convert equity and crypto str to var
TODO: check dates handling (utc, utc-3)
"""
import time
import pandas as pd
import config.info_weeks as wk
import strategies.pivotes as strategy
import analisis.newReporting as show
from tqdm import tqdm
from config import info_tickers as tk

testingMode = 'On'
pd.options.mode.chained_assignment = None  # default='warn'


def main():
    # Define what are we testing
    equity = 'equity'
    crypto = 'crypto'
    asset = equity

    # Setting Parameters
    pivotInterval = '1w'
    pivotTolerance = 0.015
    candlesInterval = '1h'
    smaFast = 7
    smaSlow = 21
    resultsList = list()
    weeks = wk.weeksTry
    resultsIntoXls = True

    # Weeks & tickers to check
    if asset == 'equity':
        tickers = tk.cedears
        tickers = ['TSLA', 'AAPL']
    else:
        tickers = tk.tickers

    # Pivot calculation
    pivotes = strategy.downloadPivotes(tickers=tickers, interval=pivotInterval, type=asset)

    # Creating initial DB to work with
    dataInit = strategy.createTestingDf(tickers=tickers,
                                        interval=candlesInterval,
                                        pivotes=pivotes,
                                        smaSlow=smaSlow,
                                        smaFast=smaFast,
                                        asset=asset,
                                        testingMode=testingMode)
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

            data = strategy.addColumns(dataInit[ticker].loc[mask])
            data = data.fillna(0)
            data.reset_index(inplace=True)
            data['Week'] = week[0]

            # Converting DataFrame to Dict
            dataDict = data.to_dict('records')

            if len(dataDict) > 0:
                ################
                # Apply strategy
                ################
                dataWithTrades = strategy.estrategiaPivots(dictValues=dataDict,
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
    filename = f'results{asset}'

    resultsDf.to_csv(filename + '.csv')
    if resultsIntoXls:
        resultsDf.to_excel(filename + '.xls')
    print(f'{filename} created')

    print(f'\nReporting')
    show.reportingView(df=resultsDf)

    try:
        show.reportingOld(interval=pivotInterval, type=asset, file=filename, weeks=weeks)
    except Exception as e:
        print(f'Nope> {e}')


if __name__ == '__main__':
    main()
