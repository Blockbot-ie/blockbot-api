from datetime import date, timedelta, datetime
from bb.models import Strategies_Suggested, Strategy
import ccxt
import pandas as pd
import san
import datetime as dt
import numpy as np
import ast

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

def get_san_data(coin, date_from, date_to, interval):
    df = san.get("ohlcv/${coin}",
                      from_date=date_from,
                      to_date=date_to,
                      interval=interval,
                      aggregation='FIRST')
    
    df = pd.DataFrame(df, columns=['openPriceUsd', 'closePriceUsd', 'highPriceUsd', 'lowPriceUsd', 'volume'])
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df.index.name = 'Opentime'
    # df.index = df.index.strftime('%Y-%m-%d')  
    df = df.sort_index()
    return df

def get_san_data_for_graphs(coin, date_from, date_to, interval):
    date_from = date_from + "-01-01T00:00:00Z"
    date_to = date_to + "-01-01T00:00:00Z"
    df = san.get("ohlcv/ethereum",
              from_date=date_from,
              to_date=date_to,
              interval="1d",
              aggregation='FIRST')
    df = df[['openPriceUsd']]
    df.columns = ['ethereum_Price']
    df.index.name = 'date'
    df.index = df.index.tz_localize(None)
    return df

def build_data_frame_for_strategy(strategy, date_from, date_to, amount):
    
    initial_investment = amount
    trade_fee = 0.005

    coin = 'bitcoin' if strategy == '3c82058e-8007-4c8d-8ff5-3561f3870653' or strategy == '3c6bd390-7e32-426b-be28-54e9e430b223' else 'ethereum'

    df = get_san_data_for_graphs(coin, str(date_from), str(date_to), '1d')
    
    # if strategy == '3c82058e-8007-4c8d-8ff5-3561f3870653':
        # construct_20_10_MA(df)

    if strategy == 'c2e1a3c4-f39e-4bdf-8094-16e5336f354a':
        data = construct_ETH_5_EMA(df, amount)
        return data
    
    if strategy == '57e7096a-511c-4531-b705-5bb40296af87':
        data = construct_ETH_5_SLOPE_EMA(df, amount)
        return data

def construct_ETH_5_EMA(df, amount):
    # -- Parameters -- #
    initial_investment = int(amount)
    trade_fee = 0.005
    # ---------------- #
    df = df.resample('d').first()
    df['eth_Price_Close'] = df['ethereum_Price'].shift(-1)
    df['ethereum_Change_Ratio'] = df['eth_Price_Close']/df['ethereum_Price']
    df['MA'] = df['ethereum_Price'].ewm(span=7*5, min_periods=7*5).mean()
    # -- Always held ethereum base-case -- #
    df['profit'] = np.where(df.index == df.index.min(), initial_investment, df['ethereum_Change_Ratio'])
    df['hodl_value'] = df['profit'].cumprod()
    # ---------------------------------- #
    # --- Above Below Strategy --- #
    df['signal'] = float('Nan')
    df.loc[df.index == df.index.min(), 'signal'] = 1
    df.loc[df['ethereum_Price'] < (df['MA'] * 0.95), 'signal'] = 0
    df.loc[(df['ethereum_Price'] > (df['MA'] * 1.05)) & (df['signal'].isnull()), 'signal'] = 1
    df['signal'] = df['signal'].ffill()
    df['trade_fee_signal1'] = df['signal'].diff(-1)
    df['trade_fee_signal2'] = np.where((df.trade_fee_signal1 == -1) | (df.trade_fee_signal1 == 1), 1, 0)
    df['Change_Ratio_New'] = df['ethereum_Change_Ratio']
    df.loc[df['signal'] == 0, 'Change_Ratio_New'] = 1
    df.loc[df['trade_fee_signal2'] == 1, 'Change_Ratio_New'] = df['Change_Ratio_New'] - trade_fee
    df['profit'] = np.where(df.index == df.index.min(), initial_investment, df['Change_Ratio_New'])
    df['strategy_value'] = df['profit'].cumprod()
    # -------------------- #
    df = df.reset_index()
    df = df[['date', 'hodl_value', 'strategy_value']]
    df['hodl_value'] = round(df['hodl_value'], 2)
    df['strategy_value'] = round(df['strategy_value'], 2)
    df = df.ffill()
    x = df.to_json(orient = "records")
    x = ast.literal_eval(x)
    return x

def construct_ETH_5_SLOPE_EMA(df, amount):
    initial_investment = int(amount)
    trade_fee = 0.005
    # ---------------- #
    df = df.resample('d').first()
    df['eth_Price_Close'] = df['ethereum_Price'].shift(-1)
    df['ethereum_Change_Ratio'] = df['eth_Price_Close']/df['ethereum_Price']
    df['MA'] = df['ethereum_Price'].ewm(span=7*5, min_periods=7*5).mean()
    df['slope'] = df['MA'] - df['MA'].shift(1)
    # -- Always held ethereum base-case -- #
    df['profit'] = np.where(df.index == df.index.min(), initial_investment, df['ethereum_Change_Ratio'])
    df['hodl_value'] = df['profit'].cumprod()
    # ---------------------------------- #
    # --- Slope Strategy --- #
    df['signal'] = float('Nan')
    df.loc[df.index == df.index.min(), 'signal'] = 1
    df.loc[df['slope'] < -0.75, 'signal'] = 0
    df.loc[df['slope'] > 0.75, 'signal'] = 1
    df['signal'] = df['signal'].ffill()
    df['trade_fee_signal1'] = df['signal'].diff(-1)
    df['trade_fee_signal2'] = np.where((df.trade_fee_signal1 == -1) | (df.trade_fee_signal1 == 1), 1, 0)
    df['Change_Ratio_New'] = df['ethereum_Change_Ratio']
    df.loc[df['signal'] == 0, 'Change_Ratio_New'] = 1
    df.loc[df['trade_fee_signal2'] == 1, 'Change_Ratio_New'] = df['Change_Ratio_New'] - trade_fee
    df['profit'] = np.where(df.index == df.index.min(), initial_investment, df['Change_Ratio_New'])
    df['strategy_value'] = df['profit'].cumprod()
    # -------------------- #
    df = df.reset_index()
    df = df[['date', 'hodl_value', 'strategy_value']]
    df['hodl_value'] = round(df['hodl_value'], 2)
    df['strategy_value'] = round(df['strategy_value'], 2)
    df = df.ffill()
    x = df.to_json(orient = "records")
    x = ast.literal_eval(x)
    return x

