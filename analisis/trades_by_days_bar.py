import pandas as pd
import os
import matplotlib.pyplot as plt
import config.info_tickers as tk

pd.set_option("display.max_columns", 10)


path = os.getcwd() + '\\'
path = 'C:\\Users\\Matias.MSI\\PycharmProjects\\backtesting\\data\\'

file = 'Detailed Results.csv'

df1 = pd.read_csv(path+file)

nBins = 500

dfResults = pd.DataFrame()

condition = df1['Obs'].isin(['Cierro Pos', 'Long Trade Active', 'Short Trade Active', 'Toca SL'])
df3 = df1.loc[condition]
df3 = df3[['openTime', 'Signal', 'Result']]
df3['Signal'] = df3['Signal'].shift()
df3['openTime'] = pd.to_datetime(df3['openTime'], format='%Y-%m-%d').dt.date
df3.set_index(['openTime'], inplace=True)


dfQty = df3.dropna()[['Signal']]
dfQty['Signal'] = 1
#dfQty.to_excel(excel_writer='movements.xlsx', sheet_name='hola')

dfQty = dfQty.groupby([dfQty.index]).sum()


fig, axs = plt.subplots(nrows=3, ncols=1)

x = dfQty.index
y = dfQty['Signal']

axs[0].bar(x, y, width=0.3)
axs[0].xaxis_date()
axs[0].set_title('Trades by Day')

dfQtyWin = df3.dropna()[['Signal', 'Result']]
dfQtyWin = dfQtyWin.loc[dfQtyWin['Result'] > 0]
dfQtyWin['Signal'] = 1
dfQtyWin = dfQtyWin.groupby([dfQtyWin.index]).sum()

x = dfQtyWin.index
y = dfQtyWin['Signal']

axs[1].bar(x, y, width=0.5, color='green')
axs[1].xaxis_date()
axs[1].set_title('Wins by Day')

dfQtyLoss = df3.dropna()[['Signal', 'Result']]
dfQtyLoss = dfQtyLoss.loc[dfQtyLoss['Result'] < 0]
dfQtyLoss['Signal'] = 1
dfQtyLoss = dfQtyLoss.groupby([dfQtyLoss.index]).sum()

x = dfQtyLoss.index
y = dfQtyLoss['Signal']

axs[2].bar(x, y, width=0.5, color='red')
axs[2].xaxis_date()
axs[2].set_title('Loss by Day')


plt.show()


