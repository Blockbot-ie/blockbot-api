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


def build_data_frame_for_strategy(strategy, date_from, date_to, amount):
    
    initial_investment = amount
    trade_fee = 0.005

    coin = 'bitcoin' if strategy == '3c82058e-8007-4c8d-8ff5-3561f3870653' or strategy == '3c6bd390-7e32-426b-be28-54e9e430b223' else 'ethereum'
    
    df = get_san_data(coin, date_from, date_to, '1d')
    
    if strategy == '3c82058e-8007-4c8d-8ff5-3561f3870653':
        construct_20_10_MA(df)





def construct_20_10_MA(df):
    df['BTC_Price_Close'] = df['Bitcoin_Price'].shift(-1)
    df['Bitcoin_Change_Ratio'] = df['BTC_Price_Close']/df['Bitcoin_Price']
    df['20_Week_MA'] = df['Bitcoin_Price'].rolling(7*20, min_periods=7*20).mean()
    df['10_Week_MA'] = df['Bitcoin_Price'].rolling(7*10, min_periods=7*10).mean()

    df['bubble'] = float('Nan')
    df.loc[df['Bitcoin_Price'] >= df['20_Week_MA']*2.5, 'bubble'] = 1
    df.loc[df['Bitcoin_Price'] < df['20_Week_MA'], 'bubble'] = 0
    df['bubble'] = df['bubble'].ffill()


    df = df.loc[date_from: date_to]

    # -- Always held Bitcoin base-case -- #
    df['profit'] = np.where(df.index == df.index.min(), initial_investment, df['Bitcoin_Change_Ratio'])
    df['Always_Hold_Bitcoin_profit'] = df['profit'].cumprod()
    df['signal'] = float('Nan')
    df.loc[df.index == df.index.min(), 'signal'] = 1
    df.loc[(df['Bitcoin_Price'] - df['20_Week_MA'] < 0) & (df['bubble'] == 0), 'signal'] = 0
    df.loc[(df['Bitcoin_Price'] - df['20_Week_MA'] > 0) & (df['bubble'] == 0), 'signal'] = 1
    df.loc[(df['Bitcoin_Price'] - df['10_Week_MA'] < 0) & (df['bubble'] == 1), 'signal'] = 0
    df.loc[(df['Bitcoin_Price'] - df['10_Week_MA'] > 0) & (df['bubble'] == 1), 'signal'] = 1
    df['signal'] = df['signal'].ffill()

    df['trade_fee_signal1'] = df['signal'].diff(-1)
    df['trade_fee_signal2'] = np.where((df.trade_fee_signal1 == -1) | (df.trade_fee_signal1 == 1), 1, 0)


    df['Change_Ratio_New'] = df['Bitcoin_Change_Ratio']
    df.loc[df['signal'] == 0, 'Change_Ratio_New'] = 1
    df.loc[df['trade_fee_signal2'] == 1, 'Change_Ratio_New'] = df['Change_Ratio_New'] - trade_fee


    df['profit'] = np.where(df.index == df.index.min(), initial_investment, df['Change_Ratio_New'])
    df['cumalative_profit'] = df['profit'].cumprod()
    # -------------------- #

    df['Extra_profit_To_Basecase'] = df['cumalative_profit'] - df['Always_Hold_Bitcoin_profit']

    df['signal'] = df['signal']*3000
    df['bubble'] = df['bubble']*3000