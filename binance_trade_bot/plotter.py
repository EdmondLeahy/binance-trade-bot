
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta, date
import time
import os
from binance.client import Client
import datetime

api_key='rxjvvkGRGUcApapeWzUFAvJhHe3lC3doIEbfqL5v75xK4Wwo2H8MiQOoYdx1lwdI'
api_secret_key='GFE02ezysvl44wWjdjL05YnpxQqz9lgGir6HEc9rcq10f0cTHSufF6kw98120Btr'

client = Client(api_key, api_secret_key)

# LOOK AT THIS : https://www.youtube.com/watch?v=37Zj955LFT0

def get_historical_data(length):
    howLong = length # Hours
    # Calculate the timestamps for the binance api function
    untilThisDate = datetime.now()
    sinceThisDate = untilThisDate - timedelta(hours = howLong)
    # Execute the query from binance - timestamps must be converted to strings !
    candle = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, str(sinceThisDate), str(untilThisDate))

    # Create a dataframe to label all the columns returned by binance so we work with them later.
    df = pd.DataFrame(candle, columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime',
                                       'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol',
                                       'ignore'])
    # as timestamp is returned in ms, let us convert this back to proper timestamps.
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms')

    # Get rid of columns we do not need
    df = df.drop(['closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol','takerBuyQuoteVol', 'ignore'], axis=1)

    return df