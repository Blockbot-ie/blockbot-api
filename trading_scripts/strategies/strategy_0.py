import datetime as dt
from bb.models import Strategies_Suggested, Strategy, Strategy_Supported_Pairs, User_Exchange_Account, User_Strategy_Pair, Exchange
import pandas as pd
from trading_scripts.services import exchange_data, helpers
import os, sys

def strategy_0_main(strategy):
    """
    Main function
    output:
    """
    try:
        strategy_pairs = Strategy_Supported_Pairs.objects.filter(strategy_id=strategy)
        for pair in strategy_pairs:
            start_time_utc = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            date_from = dt.datetime.today() + dt.timedelta(weeks=-20)
            df = exchange_data.load_prices(exchange='ftx', price_pair=pair.pair, frequency='1d', date_from=date_from)
            ma = exchange_data.get_latest_ma(df_data=df, period='w', num_of_periods=20)

            current_price = df.iloc[-1]['Close']
            
            split = pair.pair.index('/')
            first_symbol = pair.pair[:split]
            second_symbol = pair.pair[split:]
            if current_price > ma:
                target_currency = first_symbol
            else:
                target_currency = second_symbol
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

def strategy_0_buy_or_sell(strategy):
    """
    Function to buy and sell
    output:
    """
    try:
        target_currencies = helpers.get_target_currencies(strategy)
        user_strategy_pairs = User_Strategy_Pair.objects.filter(is_active=True, strategy_id=strategy)
        for user in user_strategy_pairs:
            user_exchange_account = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=user.user_exchange_account_id).first()
            exchange = Exchange.objects.filter(exchange_id=user_exchange_account.exchange_id).first()
            print(user_exchange_account.user_exchange_account_id)
            print(user_exchange_account.api_password)
            print(user_exchange_account.api_secret)
            user_exchange = helpers.get_exchange(exchange.name, user_exchange_account.api_key, user_exchange_account.api_secret, user_exchange_account.sub_account_name, user_exchange_account.api_password)
            buy = False
            sell = False
            target_currency = [x['target_currency'] for x in target_currencies if x['pair'] == user.pair][0]
            split = user.pair.index('/')
            first_symbol = user.pair[:split]
            second_symbol = user.pair[split:]
            first_symbol_balance = user_exchange.fetch_balance()
            try:
                balances = user_exchange.fetch_balance()
            except Exception as e:
                print(e)
            available_balances_usd = {}
            for balance in balances['info']['result']:
                available_balances_usd[balance['coin']] = balance['usdValue']
            print('Want to be in ', target_currency)
            if 'BTC' in balances and 'USDT' in balances:
                if available_balances_usd['BTC'] > available_balances_usd['USDT']:
                    if target_currency == 'BTC':
                        print('Condition already satisfied')
                        pass
                    else:
                        amount = balances['BTC']['free']
                        try:
                            print('Selling BTC')
                            order = exchange.create_order('BTC/USDT', 'market', 'sell', amount)
                        except Exception as e:
                            print("An exception occurred: ", e)
                            # send_email.send_daily_email(None, type(e))
                else:
                    if target_currency != 'USDT':
                        amount = 1
                        price = balances['USDT']['free']
                        try:
                            print('Buying BTC')
                            order = exchange.create_order('BTC/USDT', 'market', 'buy', amount, price)
                        except Exception as e:
                            print("An exception occurred: ", e)
                            # send_email.send_daily_email(None, type(e))
                    else:
                        print('Condition already satisfied')
                        pass
                    
            if 'BTC' in balances and 'USDT' not in balances:
                if target_currency == 'BTC':
                    print('Condition already satisfied')
                    pass
                else:
                    amount = balances['BTC']['free']
                    try:
                        print('Selling BTC')
                        order = exchange.create_order('BTC/USDT', 'market', 'sell', amount)
                    except Exception as e:
                            print("An exception occurred: ", e)
                            # send_email.send_daily_email(None, type(e))

            if 'USDT' in balances and 'BTC' not in balances:
                if target_currency == 'USDT':
                    print('Condition already satisfied')
                    pass
                else:
                    amount = 1
                    price = balances['USDT']['free']
                    try:
                        print('Buying BTC')
                        order = exchange.create_order('BTC/USDT', 'market', 'buy', amount, price)
                    except Exception as e:
                            print("An exception occurred: ", e)
                            # send_email.send_daily_email(None, type(e))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return