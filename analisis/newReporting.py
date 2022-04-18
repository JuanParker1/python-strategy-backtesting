import pandas as pd


def reporting(data, withPrint = False):
    ################
    #### DATOS
    ################

    longsQty = (data['trade'] == 'LONG') & (data['profit'] != 0)
    longsQty = data.loc[longsQty]['trade'].count()

    shortsQty = (data['trade'] == 'SHORT') & (data['profit'] != 0)
    shortsQty = data.loc[shortsQty]['trade'].count()

    tradesPos = (data['profit'] > 0)
    tradesPos = data.loc[tradesPos]['profit'].count()

    longsPos = (data['trade'] == 'LONG') & (data['profit'] > 0)
    longsPos = data.loc[longsPos]['trade'].count()

    shortsPos = (data['trade'] == 'SHORT') & (data['profit'] > 0)
    shortsPos = data.loc[shortsPos]['trade'].count()

    tradesNeg = (data['profit'] < 0)
    tradesNeg = data.loc[tradesNeg]['profit'].count()

    rendPromPos = (data['profit'] > 0)
    rendPromPos = data.loc[rendPromPos]['profit'].mean()

    rendPromNeg = (data['profit'] < 0)
    rendPromNeg = data.loc[rendPromNeg]['profit'].mean()

    #fechaIni = data['openTime'].min()
    #fechaIni = datetime.strptime(fechaIni, '%Y-%m-%d %H:%M:%S')
    #fechaIni = datetime.date(fechaIni)

    #fechaFin = data['openTime'].max()
    #fechaFin = datetime.strptime(fechaFin, '%Y-%m-%d %H:%M:%S')
    #fechaFin = datetime.date(fechaFin)
    #weeksQty = (fechaFin - fechaIni).days // 7

    rendTot = (data['profit'] != 0)
    rendTot = data.loc[rendTot]['profit'].sum().round(2)

    if withPrint:
        #################################
        ### PRINTING GOES BRRRRRRRRRRRR
        #################################

        print("\n\n## Resultados ##")
        #print(f"Periodo analizado: {fechaIni} a {fechaFin}")
        #print(f"Cantidad semanas: {weeksQty}")
        print(f"Cantidad de trades: {longsQty + shortsQty}")
        print(f"Cantidad de longs: {longsQty}")
        print(f"Cantidad de longs ganadores: {longsPos}")
        print(f"Cantidad de shorts: {shortsQty}")
        print(f"Cantidad de shorts ganadores: {shortsPos}")
        print(f"Cantidad ganadores: {tradesPos}")
        print(f"Cantidad perdedores: {tradesNeg}")

        print("\n## Rendimientos ##")
        print(f"Rendimiento Total: {round(rendTot, 2)}%")
        #print(f"Rendimiento promedio (semanal): {round(rendTot / weeksQty, 2)}%")
        print(f"Rendimiento promedio ganadores: {round(rendPromPos, 2)}")
        print(f"Rendimiento promedio perdedores: {round(rendPromNeg, 2)}")

        # print(f"\n## Volatilidad (vs {bench}) ##")

    df = pd.DataFrame(data={'P&L': round(rendTot, 2),
                            'Trades Qty': longsQty + shortsQty,
                            'Long Qty': longsQty,
                            'Shorts Qty': shortsQty,
                            'Long Wins': longsPos,
                            'Shorts Wins': shortsPos,
                            'Trades Wins': tradesPos,
                            'Trades Loss': tradesNeg,
                            'Biggest_Loss': data['profit'].min(),
                            'Biggest_Win': data['profit'].max()},
                      index=[0]
                      )

    return df



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


def reportingOld(weeks, interval, file, type='Equity'):
    import pandas as pd
    import matplotlib.pyplot as plt
    from datetime import datetime

    import warnings
    import matplotlib.cbook

    warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

    file = file + '.csv'
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
        if interval == '1M':
            interval = '1mo '

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
