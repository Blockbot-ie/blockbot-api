import datetime as dt
from bb.models import Pairs, Strategies_Suggested, Strategy, Strategy_Supported_Pairs, User_Exchange_Account, User_Strategy_Pair, Exchange, Orders
import pandas as pd
from trading_scripts.services import exchange_data, helpers
import os, sys
from time import sleep

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
            start_time_utc = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            date_from = dt.datetime.today() + dt.timedelta(weeks=-20)
            df = exchange_data.load_prices(exchange='coinbasepro', price_pair=symbol.symbol, frequency='1d', date_from=date_from)
            ma = exchange_data.get_latest_ma(df_data=df, period='w', num_of_periods=20)

            current_price = df.iloc[-1]['Close']
            
            split = symbol.symbol.index('/')
            first_symbol = symbol.symbol[:split]
            second_symbol = symbol.symbol[split:]
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
            start_time_utc = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            date_from = dt.datetime.today() + dt.timedelta(weeks=-42)
            df = exchange_data.load_prices(exchange='coinbasepro', price_pair=symbol.symbol, frequency='1d', date_from=date_from)
            # df.loc['2020-01-01': ]  # Doesn't work when prices are zero initially so avoiding 2010

            df['20_Week_MA'] = df['Close'].rolling(7*20, min_periods=7*20).mean()
            df['10_Week_MA'] = df['Close'].rolling(7*10, min_periods=7*10).mean()

            df['bubble'] = float('Nan')
            df.loc[df['Close'] >= df['20_Week_MA']*2.5, 'bubble'] = 1
            df.loc[df['Close'] < df['20_Week_MA'], 'bubble'] = 0
            df['bubble'] = df['bubble'].ffill()
            
            df['signal'] = float('Nan')
            df.loc[df.index == df.index.min(), 'signal'] = 1
            df.loc[(df['Close'] - df['20_Week_MA'] < 0) & (df['bubble'] == 0), 'signal'] = 0
            df.loc[(df['Close'] - df['20_Week_MA'] > 0) & (df['bubble'] == 0), 'signal'] = 1
            df.loc[(df['Close'] - df['10_Week_MA'] < 0) & (df['bubble'] == 1), 'signal'] = 0
            df.loc[(df['Close'] - df['10_Week_MA'] > 0) & (df['bubble'] == 1), 'signal'] = 1
            df['signal'] = df['signal'].ffill()
        
            split = symbol.symbol.index('/')
            first_symbol = symbol.symbol[:split]
            second_symbol = symbol.symbol[split:]
            if df.iloc[-1]['signal'] == 1:
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