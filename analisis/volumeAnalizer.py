import pandas as pd
import os
import matplotlib.pyplot as plt
import config.tickers as tk

pd.set_option("display.max_columns", 10)


path = os.getcwd() + '\\'
path = 'C:\\Users\\Matias.MSI\\PycharmProjects\\backtesting\\data\\'

file = 'Detailed Results.csv'

df1 = pd.read_csv(path+file)

nBins = 500

dfResults = pd.DataFrame()


tickers = ['ALICEUSDT', 'BTCUSDT', 'ETHUSDT']

for ticker in tickers:
    condition = df1['Ticker'] == ticker
    df3 = df1.loc[condition]

    condition = df3['Obs'].isin(['Cierro Pos', 'Long Trade Active', 'Short Trade Active', 'Toca SL'])
    df3 = df3.loc[condition]

    df3.set_index('openTime', inplace=True)

    df3['Signal'] = df3['Signal'].shift()
    df3['VolOp'] = df3['Volume'].shift()
    df3['VolOpMA'] = df3['VolumeMA'].shift()

    df3 = df3[['Signal', 'PE', 'SL', 'Result', 'VolOpMA', 'VolOp']]
    df3.to_excel(excel_writer='Resumen por Ticker.xlsx', sheet_name='Resultados')

    cond1 = df3['Signal'] == 'Long'
    cond2 = df3['Signal'] == 'Short'

    condVolMay = df3['VolOp'] > df3['VolOpMA']
    condVolMen = df3['VolOp'] < df3['VolOpMA']

    cond4 = df3['Result'] > 0
    cond5 = df3['Result'] < 0

    totalMov = len(df3.index)

    longsPos = len(df3.loc[cond1 & cond4])
    longsNeg = len(df3.loc[cond1 & cond5])
    longsPosVol = len(df3.loc[cond1 & cond4 & condVolMay])
    longsNegVol = len(df3.loc[cond1 & cond5 & condVolMen])

    shortsPos = len(df3.loc[cond2 & cond4])
    shortsNeg = len(df3.loc[cond2 & cond5])
    shortsPosVol = len(df3.loc[cond2 & cond4 & condVolMay])
    shortsNegVol = len(df3.loc[cond2 & cond5 & condVolMen])

    try:
        longsBuenos = f'{round(longsPosVol / longsPos * 100, 2)}%'
    except:
        longsBuenos = '-'

    try:
        longsMalos = f'{round(longsNegVol / longsNeg * 100, 2)}%'
    except:
        longsMalos = '-'

    try:
        shortsBuenos = f'{round(shortsPosVol / shortsPos * 100, 2)}%'
    except:
        shortsBuenos = '-'

    try:
        shortsMalos = f'{round(shortsNegVol / shortsNeg * 100, 2)}%'
    except:
        shortsMalos = '-'

    dfAux = {'Total Mov': totalMov,
             'Longs Pos': longsPos,
             'Longs Pos c/vol': longsPosVol,
             'Longs Buenos (%)': longsBuenos,
             'Longs Neg': longsNeg,
             'Longs Neg s/vol': longsNegVol,
             'Longs Malos (%)': longsMalos,

             'Shorts Pos': shortsPos,
             'Shorts Pos c/Vol': shortsPosVol,
             'Shorts Buenos (%)': shortsBuenos,
             'Shorts Neg': shortsNeg,
             'Shorts Neg s/Vol': shortsNegVol,
             'Shorts Malos (%)': shortsMalos
             }
    dfAux = pd.DataFrame(data=dfAux, index=[ticker])

    dfResults = dfResults.append(dfAux)

dfResults.to_excel(excel_writer='Resumen por Moneda.xlsx', sheet_name='Resultados')
'''
print(f'Total movimientos: {totalMov}')
print(f'Longs positivos: {longsPos}')
print(f'Longs positivos c/volumen: {longsPosVol} - {round(longsPosVol / longsPos * 100, 2)}%')
print(f'Longs negativos: {longsNeg}')
print(f'Longs negativos c/volumen: {longsNegVol} - {round(longsNegVol / longsNeg * 100, 2)}%')
print(f'Shorts positivos: {shortsPos}')
print(f'Shorts positivos c/volumen: {shortsPosVol} - {round(shortsPosVol / shortsPos * 100, 2)}%')
print(f'Shorts negativos: {shortsNeg}')
print(f'Shorts negativos c/volumen: {shortsNegVol} - {round(shortsNegVol / shortsNeg * 100, 2)}%')
'''

'''
fig, axs = plt.subplots(nrows=2, ncols=1)

axs[0].hist(df3['Result'], bins=n_bins)
axs[0].set_title('Results by Volume')

axs[1].hist(df3['Result'], bins=n_bins)
axs[1].set_title('Results by Volume')
'''

plt.show()
