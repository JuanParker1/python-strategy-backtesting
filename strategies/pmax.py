import config.technical_analysis as ta


def applyPmaxStd(data, atrMultiplier, maType, source, atrPeriod, atrMa, maLength):
    print(f'Adding indicators')
    data = ta.addSource(data, source)
    data = ta.addAtr(data, atrPeriod, atrMa)
    data = ta.addMaByType(data, source, maType, maLength)

    print(f'Setting columns')
    data['trade'] = prevTrade = ''
    data['entry'] = prevEntry = 0
    data['stop'] = prevStop = 0
    data['profit'] = 0
    data['longStop'] = data['calcLongStop'] = 0
    data['shortStop'] = data['calcShortStop'] = 99999999
    prevLongStop = 0
    prevShortStop = 99999999

    data['atrMultiplier'] = atrMultiplier

    # convert df into dict to backtest faster
    values_list = list()
    dataDict = data.to_dict('records')

    print(f'Calculating values')
    for row in dataDict:
        row['trade'] = prevTrade
        row['entry'] = prevEntry
        row['stop'] = prevStop

        row['calcLongStop'] = row[maType] - atrMultiplier * row['atr']
        row['calcShortStop'] = row[maType] + atrMultiplier * row['atr']

        # Define Long Stop Loses
        slLongValues = [prevLongStop, row['calcLongStop'], row['longStop']]

        row['longStop'] = max(slLongValues)

        prevLongStop = row['longStop']

        # Define Short Stop Loses
        slShortValues = [prevShortStop, row['calcShortStop'], row['shortStop']]
        row['shortStop'] = min(slShortValues)

        prevShortStop = row['shortStop']

        #
        # Handling longs
        #
        if (row[maType] > row['shortStop']) & (row['trade'] not in ('LONG', 'SHORT')):
            row['trade'] = prevTrade = 'LONG'
            row['entry'] = prevEntry = row['Close']
            row['stop'] = prevStop = row['longStop']

        if row['trade'] == 'LONG':
            prevShortStop = 999999999

            if row[maType] <= row['longStop']:
                row['profit'] = (row['Close'] - row['entry']) * 100 / row['entry']
                prevTrade = ''
                prevEntry = 0
                prevStop = 0

        #
        # Handling shorts
        #
        if (row[maType] < row['longStop']) & (row['trade'] not in ('LONG', 'SHORT')):
            row['trade'] = prevTrade = 'SHORT'
            row['entry'] = prevEntry = row['Close']
            row['stop'] = prevStop = row['shortStop']

        if row['trade'] == 'SHORT':
            prevLongStop = 0

            if row[maType] >= row['shortStop']:
                row['profit'] = (row['entry'] - row['Close']) * 100 / row['entry']
                prevTrade = ''
                prevEntry = 0
                prevStop = 0

        # Create results
        values_list.append(row)

    return values_list


def applyPmaxPsar(data, atrMultiplier, maType, source, atrPeriod, atrMa, maLength):
    print(f'Adding indicators')
    data = ta.addSource(data, source)
    data = ta.addAtr(data, atrPeriod, atrMa)
    data = ta.addMaByType(data, source, maType, maLength)
    data = ta.addPsar(data)

    print(f'Setting columns')
    data['trade'] = prevTrade = ''
    data['entry'] = prevEntry = 0
    data['stop'] = prevStop = 0
    data['profit'] = 0
    data['longStop'] = data['calcLongStop'] = 0
    data['shortStop'] = data['calcShortStop'] = 99999999
    prevLongStop = 0
    prevShortStop = 99999999

    data['atrMultiplier'] = atrMultiplier

    # convert df into dict to backtest faster
    values_list = list()
    dataDict = data.to_dict('records')

    print(f'Calculating values')
    for row in dataDict:
        row['trade'] = prevTrade
        row['entry'] = prevEntry
        row['stop'] = prevStop

        row['calcLongStop'] = row[maType] - atrMultiplier * row['atr']
        row['calcShortStop'] = row[maType] + atrMultiplier * row['atr']

        # Define Long Stop Loses
        if row['psarl'] > row['Close']:
            row['psarl'] = 0

        slLongValues = [prevLongStop, row['calcLongStop'], row['longStop'], row['psarl']]

        row['longStop'] = max(slLongValues)

        prevLongStop = row['longStop']

        # Define Short Stop Loses
        if row['psars'] < row['Close']:
            row['psars'] = 999999999

        slShortValues = [prevShortStop, row['calcShortStop'], row['shortStop'], row['psars']]

        row['shortStop'] = min(slShortValues)

        prevShortStop = row['shortStop']

        #
        # Handling longs
        #
        if (row[maType] > row['shortStop']) & (row['trade'] not in ('LONG', 'SHORT')):
            row['trade'] = prevTrade = 'LONG'
            row['entry'] = prevEntry = row['Close']
            row['stop'] = prevStop = row['longStop']

        if row['trade'] == 'LONG':
            prevShortStop = 999999999

            if row[maType] <= row['longStop']:
                row['profit'] = (row['Close'] - row['entry']) * 100 / row['entry']
                prevTrade = ''
                prevEntry = 0
                prevStop = 0

        #
        # Handling shorts
        #
        if (row[maType] < row['longStop']) & (row['trade'] not in ('LONG', 'SHORT')):
            row['trade'] = prevTrade = 'SHORT'
            row['entry'] = prevEntry = row['Close']
            row['stop'] = prevStop = row['shortStop']

        if row['trade'] == 'SHORT':
            prevLongStop = 0

            if row[maType] >= row['shortStop']:
                row['profit'] = (row['entry'] - row['Close']) * 100 / row['entry']
                prevTrade = ''
                prevEntry = 0
                prevStop = 0

        # Create results
        values_list.append(row)

    return values_list


def applyPmaxFixedSl(data, atrMultiplier, maType, source, atrPeriod, atrMa, maLength):
    print(f'Adding indicators')
    data = ta.addSource(data, source)
    data = ta.addAtr(data, atrPeriod, atrMa)
    data = ta.addMaByType(data, source, maType, maLength)

    print(f'Setting columns')
    data['trade'] = prevTrade = ''
    data['entry'] = prevEntry = 0
    data['stop'] = prevStop = 0
    data['profit'] = 0
    data['longStop'] = data['calcLongStop'] = 0
    data['shortStop'] = data['calcShortStop'] = 99999999
    prevLongStop = 0
    prevShortStop = 99999999

    data['atrMultiplier'] = atrMultiplier

    # convert df into dict to backtest faster
    values_list = list()
    dataDict = data.to_dict('records')

    print(f'Calculating values')
    for row in dataDict:
        row['trade'] = prevTrade
        row['entry'] = prevEntry
        row['stop'] = prevStop

        row['calcLongStop'] = row[maType] - atrMultiplier * row['atr']
        row['calcShortStop'] = row[maType] + atrMultiplier * row['atr']

        row['maxLongSl'] = row['Close'] * 0.9
        row['maxShortSl'] = row['Close'] * 1.1

        # Define Long Stop Loses
        slLongValues = [prevLongStop, row['calcLongStop'], row['longStop'], row['maxLongSl']]

        row['longStop'] = max(slLongValues)

        prevLongStop = row['longStop']

        # Define Short Stop Loses
        slShortValues = [prevShortStop, row['calcShortStop'], row['shortStop'], row['maxShortSl']]
        row['shortStop'] = min(slShortValues)

        prevShortStop = row['shortStop']

        #
        # Handling longs
        #
        if (row[maType] > row['shortStop']) & (row['trade'] not in ('LONG', 'SHORT')):
            row['trade'] = prevTrade = 'LONG'
            row['entry'] = prevEntry = row['Close']
            row['stop'] = prevStop = row['longStop']

        if row['trade'] == 'LONG':
            prevShortStop = 999999999
            row['stop'] = prevStop = row['longStop']

            if row[maType] <= row['longStop']:
                row['profit'] = (row['Close'] - row['entry']) * 100 / row['entry']
                prevTrade = ''
                prevEntry = 0
                prevStop = 0

        #
        # Handling shorts
        #
        if (row[maType] < row['longStop']) & (row['trade'] not in ('LONG', 'SHORT')):
            row['trade'] = prevTrade = 'SHORT'
            row['entry'] = prevEntry = row['Close']
            row['stop'] = prevStop = row['shortStop']

        if row['trade'] == 'SHORT':
            prevLongStop = 0
            row['stop'] = prevStop = row['shortStop']

            if row[maType] >= row['shortStop']:
                row['profit'] = (row['entry'] - row['Close']) * 100 / row['entry']
                prevTrade = ''
                prevEntry = 0
                prevStop = 0

        # Create results
        values_list.append(row)

    return values_list
