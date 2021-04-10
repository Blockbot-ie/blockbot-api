from datetime import date, timedelta, datetime
from bb.models import Strategies_Suggested, Strategy
import ccxt
import pandas as pd
import san

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

    df = df.loc[df.index >= date_to]
    ma = df['Close'].mean()

    return ma

def load_prices(exchange, price_pair, frequency, date_from, date_to):
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
    to_timestamp = exchange.parse8601(date_to)
    candles = exchange.fetch_ohlcv(price_pair, frequency, from_timestamp, to_timestamp)
    df = pd.DataFrame(candles, columns=['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Opentime'] = pd.to_datetime(df['Opentime'], unit='ms')
    # df.set_index('Opentime', inplace=True)

    return df

def get_san_data():
    df = san.get("ohlcv/bitcoin",
                      from_date="2017-01-01T00:00:00Z",
                      to_date="2020-01-01T00:00:00Z",
                      interval="1d",
                      aggregation='FIRST')
    
    df = pd.DataFrame(df, columns=['openPriceUsd', 'closePriceUsd', 'highPriceUsd', 'lowPriceUsd', 'volume'])
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df.index.name = 'Opentime'
    df.index = df_san_bitcoin_d.index.strftime('%Y-%m-%d')
    df.index = df.index.tz_localize(None)
    df = df.sort_index()
    return df