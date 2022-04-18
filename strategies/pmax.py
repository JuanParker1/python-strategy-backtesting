
def applyStrategy(data, multiplier, maType):
    # setting needed columns
    data['trade'] = prevTrade = ''
    data['entry'] = prevEntry = 0
    data['stop'] = prevStop = 0
    data['profit'] = 0
    data['longStop'] = data['calcLongStop'] = 0
    data['shortStop'] = data['calcShortStop'] = 99999999
    prevLongStop = 0
    prevShortStop = 99999999

    data['atrMultiplier'] = multiplier

    # convert df into dict to backtest faster
    values_list = list()
    dataDict = data.to_dict('records')

    for row in dataDict:
        row['trade'] = prevTrade
        row['entry'] = prevEntry
        row['stop'] = prevStop

        row['calcLongStop'] = row[maType] - multiplier * row['atr']
        row['calcShortStop'] = row[maType] + multiplier * row['atr']

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
            row['stop'] = prevStop = row['longStop']

        if row['trade'] == 'SHORT':
            prevLongStop = 0

            if row[maType] >= row['shortStop']:
                row['profit'] = -1 * (row['entry'] - row['Close']) * 100 / row['entry']
                prevTrade = ''
                prevEntry = 0
                prevStop = 0

        # Create results
        values_list.append(row)

    return values_list