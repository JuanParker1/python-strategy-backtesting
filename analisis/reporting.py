import pandas as pd
import os
import matplotlib.pyplot as plt
import config.weeks as wk
import config.tickers as tk
from datetime import datetime, timedelta

import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

tickers = tk.theBest
weeks = wk.weeks

path = os.getcwd() + '\\data\\'
path = 'C:\\Users\\Matias.MSI\\PycharmProjects\\backtesting\\data\\'

file = 'resultsEqty.csv'
data = pd.read_csv(path+file)


################
#### SHARPE
################

btcHist = pd.read_csv('C:\\Users\\Matias.MSI\\PycharmProjects\\backtesting\\config\\csv\\BTCUSDT-1w.csv')
btcHist['Var'] = btcHist['Close'].pct_change() * 100

tasaLibreRiesgo = 0.01 / 360

rendBTC = btcHist['Var'].sum()
rendimientoBtc = btcHist['Var'].mean()
desvioBtc = btcHist['Var'].std()
sharpeBtc = (rendimientoBtc - tasaLibreRiesgo)/desvioBtc


rendimientos = data['Result'].mean()
desvios = data['Result'].std()
sharpe = (rendimientos - tasaLibreRiesgo)/desvios

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

weeksQty = (fechaFin-fechaIni).days//7

rendTot = (data['Result'] != 0)
rendTot = data.loc[rendTot]['Result'].sum().round(2)


#################################
### BEST AND WORSE
#################################

data = data.sort_values(by=['openTime'], ascending=False)

###### BEST  #########

best10Pos = data[['Ticker', 'Result' , 'Signal', 'PE', 'SL', 'openTime']].loc[data['Result'] > 0]
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

worst10Pos = data[['Ticker', 'Result' , 'Signal', 'PE', 'SL', 'openTime']].loc[data['Result'] < 0]
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
print(f"Cantidad de trades: {longsQty+shortsQty}")
print(f"Cantidad de longs: {longsQty}")
print(f"Cantidad de shorts: {shortsQty}")
print(f"Cantidad ganadores: {tradesPos}")
print(f"Cantidad perdedores: {tradesNeg}")

print("\n## Rendimientos ##")
print(f"Rendimiento Total: {round(rendTot, 2)}%")
print(f"Rendimiento promedio (semanal): {round(rendTot/weeksQty, 2)}%")
print(f"Rendimiento promedio ganadores: {round(rendPromPos, 2)}")
print(f"Rendimiento promedio perdedores: {round(rendPromNeg, 2)}")

print(f"\n## Volatilidad (vs BTC) ##")

df = pd.DataFrame(data={'BTC': [f'{round(rendBTC, 2)}%',
                                f'{round(rendBTC/weeksQty, 2)}%',
                                f'{round(sharpeBtc*7, 6)}'],
                        'Estrategia': [f'{round(rendTot, 2)}%',
                                       f'{round(rendTot/weeksQty, 2)}%',
                                       f'{round(sharpe*7, 6)}']},
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

weeklyResultsdf = list([[0,0]])

for week in weeks:

    cond1 = data['openTime'] >= week[0]
    cond2 = data['openTime'] < week[1]

    df = data.loc[cond1 & cond2]

    weeklyResultsdf.append([week[0], df['Result'].sum()])


weeklyResultsdf = pd.DataFrame(data=weeklyResultsdf)
weeklyResultsdf.columns = ['Semana', 'Resultado']
weeklyResultsdf['Acumulado'] = weeklyResultsdf['Resultado'].cumsum()
weeklyResultsStrat = weeklyResultsdf[['Acumulado']]

btcHist['Acumulado'] = btcHist['Var'].cumsum()
weeklyResultsBtc = btcHist[['Acumulado']]


#################################
###  REPORTING PLOTING
#################################

fig, axs = plt.subplots(nrows=3, ncols=2)

# Variación Capital
axs[0][0].plot(weeklyResultsStrat['Acumulado'])
axs[0][0].set_xlabel('Semana')
axs[0][0].set_title('Variación semanal del capital')

weeklyResultsdf['Resultado'].plot(ax=axs[1][0], kind='bar', width=0.1, title='').set_xlabel('')

# Variación BTC
axs[0][1].plot(weeklyResultsBtc['Acumulado'])
axs[0][1].set_xlabel('Semana')
axs[0][1].set_title('Variación semanal de BTC')

btcHist['Var'].plot(ax=axs[1][1], kind='bar', width=0.1, title='').set_xlabel('')

# Rendimiento comparado
df = pd.DataFrame(data={'BTC': [round(rendBTC, 2)],
                        'Estrategia': [round(rendTot, 2)]},
                  index=[''])

df.plot(ax=axs[2][0], kind='bar', width=0.1, title='Rendimiento (%)').set_xlabel('Rendimiento')

# Sharpe
df = pd.DataFrame(data={'BTC': [round(sharpeBtc*7, 6)],
                        'Estrategia': [round(sharpe*7, 6)]},
                  index=[''])

df.plot(ax=axs[2][1], kind='bar', width=0.1, title='Sharpe Semanal').set_xlabel('Sharpe Ratio')


plt.show()


