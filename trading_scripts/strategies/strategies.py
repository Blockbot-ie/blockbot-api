import datetime as dt
from bb.models import Pairs, Strategies_Suggested, Strategy, Strategy_Supported_Pairs, User_Exchange_Account, User_Strategy_Pair, Exchange, Orders
import pandas as pd
from trading_scripts.services import exchange_data, helpers
import os, sys
from time import sleep
import san
import numpy as np

def twenty_MA(strategy):
    """
    Main function
    output:
    """
    try:
        print('Starting 20 MA script')
        strategy_pairs = Strategy_Supported_Pairs.objects.filter(strategy_id=strategy)
        for pair in strategy_pairs:
            symbol = Pairs.objects.filter(pair_id=pair.pair_id).first()
            date_from = dt.datetime.today() + dt.timedelta(weeks=-20)
            date_to = dt.datetime.today()
            df = exchange_data.load_prices(exchange='coinbasepro', price_pair=symbol.symbol, frequency='1d', date_from=date_from, date_to=date_to)
            ma = exchange_data.get_latest_ma(df_data=df, period='w', num_of_periods=20)

            current_price = df.iloc[-1]['Close']
            
            split = symbol.symbol.index('/')
            first_symbol = symbol.symbol[:split]
            second_symbol = symbol.symbol[split+1:]
            if current_price > ma:
                target_currency = first_symbol
            else:
                target_currency = second_symbol
            # target_currency = 'USDC'
            data = Strategies_Suggested()
            data.start_time_utc = start_time_utc
            data.target_currency = target_currency
            data.tick = dt.datetime.utcnow()
            data.pair = pair
            print('Inserting into bb_strategies_suggested: ', data)
            data.save()
            print("1 item inserted successfully")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return       

def twenty_ten_MA(strategy):
    """
    Main function
    output:
    """
    try:
        print('Starting 20/10 MA script')
        strategy_pairs = Strategy_Supported_Pairs.objects.filter(strategy_id=strategy)
        for pair in strategy_pairs:
            symbol = Pairs.objects.filter(pair_id=pair.pair_id).first()
            date_from = dt.datetime.today() + dt.timedelta(weeks=-30)
            date_to = dt.datetime.today()
            df = exchange_data.load_prices(exchange='coinbasepro', price_pair=symbol.symbol, frequency='1d', date_from=date_from, date_to=date_to)
            # df.loc['2020-01-01': ]  # Doesn't work when prices are zero initially so avoiding 2010

            df['20_Week_MA'] = df['Open'].rolling(7*20, min_periods=7*20).mean()
            df['10_Week_MA'] = df['Close'].rolling(7*10, min_periods=7*10).mean()

            df['bubble'] = float('Nan')
            df.loc[df['Open'] >= df['20_Week_MA']*2.5, 'bubble'] = 1
            df.loc[df['Open'] < df['20_Week_MA'], 'bubble'] = 0
            df['bubble'] = df['bubble'].ffill()
            
            df['signal'] = float('Nan')
            df.loc[df.index == df.index.min(), 'signal'] = 1
            df.loc[(df['Open'] - df['20_Week_MA'] < 0) & (df['bubble'] == 0), 'signal'] = 0
            df.loc[(df['Open'] - df['20_Week_MA'] > 0) & (df['bubble'] == 0), 'signal'] = 1
            df.loc[(df['Open'] - df['10_Week_MA'] < 0) & (df['bubble'] == 1), 'signal'] = 0
            df.loc[(df['Open'] - df['10_Week_MA'] > 0) & (df['bubble'] == 1), 'signal'] = 1
            df['signal'] = df['signal'].ffill()

            update_target_currency(symbol.symbol, df.iloc[-1]['signal'], pair)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return

def multi_ma(strategy):
    """
    Main multi_ma function
    output:
    """
    try:
        print('Starting Multi script')
        strategy_pairs = Strategy_Supported_Pairs.objects.filter(strategy_id=strategy)
        for pair in strategy_pairs:
            symbol = Pairs.objects.filter(pair_id=pair.pair_id).first()
            start_date = dt.datetime.today()
            san_df = exchange_data.get_san_data('bitcoin', '2017-01-01T00:00:00Z', '2020-01-01T00:00:00Z', '1d')
            weeks = 200
            df = pd.DataFrame()
            while weeks > 0:
                date_from = start_date + dt.timedelta(weeks=-weeks)
                date_to = start_date + dt.timedelta(weeks=-weeks+40)
                df = df.append(exchange_data.load_prices(exchange='coinbasepro', price_pair='BTC/USDC', frequency='1d', date_from=date_from, date_to=date_to))
                weeks -= 40
            df['Opentime'] = pd.to_datetime(df['Opentime'])
            df = df.set_index('Opentime')
            df = df.sort_index()
            san_df.index = pd.to_datetime(san_df.index)
            san_df = san_df.loc[san_df.index < df.index.min()]
            df = pd.concat([df, san_df])
            df = df.sort_index()
            df = df[~df.index.duplicated(keep='first')]
            df['20_Week_MA'] = df['Open'].rolling(7*20, min_periods=7*20).mean()
            df['15_Week_MA'] = df['Open'].rolling(7*15, min_periods=7*15).mean()
            df['10_Week_MA'] = df['Open'].rolling(7*10, min_periods=7*10).mean()
            df['8_Week_MA'] = df['Open'].rolling(7*8, min_periods=7*8).mean()
            df['5_Week_MA'] = df['Open'].rolling(7*5, min_periods=7*5).mean()
            df['3_Week_MA'] = df['Open'].rolling(7*3, min_periods=7*3).mean()
            df['1_Week_MA'] = df['Open'].rolling(7*1, min_periods=7*1).mean()
            df['200_Day_MA'] = df['Open'].rolling(200, min_periods=200).mean()
            df['200_Week_MA'] = df['Open'].rolling(7*200, min_periods=7*200).mean()
            df['bubble'] = float('Nan')
            df.loc[df['Open'] >= df['20_Week_MA']*2.5, 'bubble'] = 1
            df.loc[df['Open'] < df['20_Week_MA'], 'bubble'] = 0
            df['bubble'] = df['bubble'].ffill()
            df['bubble5'] = np.where(df['Open'] > df['200_Week_MA'] * 5, 1, 0)
            df['bubble75'] = np.where(df['Open'] > df['200_Week_MA'] * 7.5, 1, 0)
            df['bubble10'] = float('Nan')
            df.loc[df['Open'] > df['200_Week_MA'] * 10, 'bubble10'] = 1
            df.loc[df['Open'] < df['20_Week_MA'], 'bubble10'] = 0
            df['bubble10'] = df['bubble10'].ffill()
            df['Week_MA'] = float('Nan')
            df.loc[df['bubble10'] == 0, 'Week_MA'] = 20
            # New Multiple MA signal calc
            for week in [10, 8, 5, 3]:
                df['Week_MA_1'] = df['Week_MA']
                df.loc[(df['Open'] < df['{0}_Week_MA'.format(week)]) & (df['Week_MA_1'].isnull()), 'Week_MA_1'] = week
                df['Week_MA_1'] = df['Week_MA_1'].ffill()
                df.loc[(df['Week_MA'].isnull()) & (df['Week_MA_1'] == week), 'Week_MA'] = df['Week_MA_1']
            df['Week_MA'] = df['Week_MA'].fillna(1)
            df['Bull_Run'] = 20
            df.loc[(df['bubble5'] == 1), 'Bull_Run'] = 15
            df.loc[(df['bubble75'] == 1), 'Bull_Run'] = 10
            df.loc[(df['bubble10'] == 1), 'Bull_Run'] = 5
            df.loc[df['Week_MA'] == 20, 'Week_MA'] = df['Bull_Run']
            df['signal'] = float('Nan')
            df.loc[df.index == df.index.min(), 'signal'] = 1
            df.loc[(df['Open'] - df['20_Week_MA'] < 0) & (df['Week_MA'] == 20), 'signal'] = 0
            df.loc[(df['Open'] - df['20_Week_MA'] > 0) & (df['Week_MA'] == 20), 'signal'] = 1
            df.loc[(df['Open'] - df['15_Week_MA'] < 0) & (df['Week_MA'] == 15), 'signal'] = 0
            df.loc[(df['Open'] - df['15_Week_MA'] > 0) & (df['Week_MA'] == 15), 'signal'] = 1
            df.loc[(df['Open'] - df['10_Week_MA'] < 0) & (df['Week_MA'] == 10), 'signal'] = 0
            df.loc[(df['Open'] - df['10_Week_MA'] > 0) & (df['Week_MA'] == 10), 'signal'] = 1
            df.loc[(df['Open'] - df['8_Week_MA'] < 0) & (df['Week_MA'] == 8), 'signal'] = 0
            df.loc[(df['Open'] - df['8_Week_MA'] > 0) & (df['Week_MA'] == 8), 'signal'] = 1
            df.loc[(df['Open'] - df['5_Week_MA'] < 0) & (df['Week_MA'] == 5), 'signal'] = 0
            df.loc[(df['Open'] - df['5_Week_MA'] > 0) & (df['Week_MA'] == 5), 'signal'] = 1
            df.loc[(df['Open'] - df['3_Week_MA'] < 0) & (df['Week_MA'] == 3), 'signal'] = 0
            df.loc[(df['Open'] - df['3_Week_MA'] > 0) & (df['Week_MA'] == 3), 'signal'] = 1
            df.loc[(df['Open'] - df['1_Week_MA'] < 0) & (df['Week_MA'] == 1), 'signal'] = 0
            df.loc[(df['Open'] - df['1_Week_MA'] > 0) & (df['Week_MA'] == 1), 'signal'] = 1
            df['signal'] = df['signal'].ffill()
            
            update_target_currency(symbol.symbol, df.iloc[-1]['signal'], pair)
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return


def eth_5_EMA(strategy):
    """
    Main eth_5_EMA function
    output:
    """
    try:
        print('Starting eth_5_EMA script')
        strategy_pairs = Strategy_Supported_Pairs.objects.filter(strategy_id=strategy)
        for pair in strategy_pairs:
            symbol = Pairs.objects.filter(pair_id=pair.pair_id).first()
            start_time_utc = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)

            date_from = dt.datetime.today() + dt.timedelta(weeks=-30)
            date_to = dt.datetime.today()
            df = exchange_data.load_prices(exchange='coinbasepro', price_pair=symbol.symbol, frequency='1d', date_from=date_from, date_to=date_to)
            df['MA'] = df['Open'].ewm(span=7*5, min_periods=7*5).mean()
            df['signal'] = float('Nan')
            df.loc[df.index == df.index.min(), 'signal'] = 1

            df.loc[df['Open'] < (df['MA'] * 0.95), 'signal'] = 0
            df.loc[(df['Open'] > (df['MA'] * 1.05)) & (df['signal'].isnull()), 'signal'] = 1

            df['signal'] = df['signal'].ffill()

            update_target_currency(symbol.symbol, df.iloc[-1]['signal'], pair)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return

def update_target_currency(pair, signal, strategy_pair):
    start_time_utc = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    split = pair.index('/')
    first_symbol = pair[:split]
    second_symbol = pair[split+1:]
    if signal == 1:
        target_currency = first_symbol
    else:
        target_currency = second_symbol
    # target_currency = 'USDC'
    data = Strategies_Suggested()
    data.start_time_utc = start_time_utc
    data.target_currency = target_currency
    data.tick = dt.datetime.utcnow()
    data.pair = strategy_pair
    print('Inserting into bb_strategies_suggested: ', data)
    data.save()
    print("1 item inserted successfully")