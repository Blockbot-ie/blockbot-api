from datetime import date, timedelta, datetime
from bb.models import Strategies_Suggested, Strategy
import ccxt
import pandas as pd

def get_latest_ma(df_data=None, period=None, num_of_periods=None):
    """
    returns the most resent MA

    param: exchange
    param: price_pair
    param: frequency
    param: date_from
    output:
    """

    print('Calulating Latest Moving Average')

    df = df_data.copy()

    seconds = num_of_periods if period in ['s', '1s'] else 0
    minutes = num_of_periods if period in ['min', '1min'] else 0
    hours = num_of_periods if period in ['h', '1h'] else 0
    days = num_of_periods if period in ['d', '1d'] else 0
    weeks = num_of_periods if period in ['w', '1w'] else 0

    date_to = df.index.max() - timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

    print(date_to)

    df = df.loc[df.index >= date_to]
    ma = df['Close'].mean()

    print(date_to)

    return ma

def load_prices(exchange, price_pair, frequency, date_from):
    """
    Function to query coin prices

    param: exchange
    param: price_pair
    param: frequency
    param: date_from
    output:
    """

    print('Getting candle data from ', exchange)

    exchange = getattr (ccxt, exchange) ()
    date_from = str(date_from)
    date_from = date_from+' 00:00:00'
    from_timestamp = exchange.parse8601(date_from)
    print(from_timestamp)
    candles = exchange.fetch_ohlcv(price_pair, frequency, from_timestamp)
    df = pd.DataFrame(candles, columns=['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Opentime'] = pd.to_datetime(df['Opentime'], unit='ms')
    df.set_index('Opentime', inplace=True)

    return df
