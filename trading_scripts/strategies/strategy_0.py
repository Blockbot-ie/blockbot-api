import datetime as dt
from bb.models import Pairs, Strategies_Suggested, Strategy, Strategy_Supported_Pairs, User_Exchange_Account, User_Strategy_Pair, Exchange, Orders
import pandas as pd
from trading_scripts.services import exchange_data, helpers
import os, sys
from time import sleep

def strategy_0_main(strategy):
    """
    Main function
    output:
    """
    try:
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
            user_exchange = helpers.get_exchange(exchange.name, user_exchange_account.api_key, user_exchange_account.api_secret, user_exchange_account.sub_account_name, user_exchange_account.api_password)
            target_currency = [x['target_currency'] for x in target_currencies if x['pair'] == user.pair][0]
            split = user.pair.index('/')
            first_symbol = user.pair[:split]
            second_symbol = user.pair[split+1:]
            try:
                balances = user_exchange.fetch_balance()
            except Exception as e:
                print(e)
            
            first_symbol_balance = balances['total'][first_symbol]
            second_symbol_balance = balances['total'][second_symbol]
            print('Want to be in ', target_currency)
            
            if target_currency == user.current_currency:
                print('Condition already satisfied')
                pass
            else:
                if target_currency == first_symbol:
                    print('Buying ', target_currency)
                    amount = 1
                    price = user.current_currency_balance
                    try:
                        order = user_exchange.create_order(user.pair, 'market', 'buy', amount, price)
                        if order:
                            price = user_exchange.fetch_ticker(user.pair)
                            new_order = Orders()
                            print(order)
                            new_order.order_id = order['id']
                            new_order.market = order['symbol']
                            new_order.side = order['side']
                            new_order.size = order['info']['specified_funds']
                            new_order.filled = order['filled']
                            new_order.filled_price = price['close']
                            new_order.fee = round(order['fee']['cost'], 2)
                            new_order.status = order['status']
                            new_order.amount = order['amount']
                            new_order.user_strategy_pair = user
                            new_order.user = user.user
                            new_order.save()

                    except Exception as e:
                        print("An exception occurred: ", e)
                        # send_email.send_daily_email(None, type(e))
                
                elif target_currency == second_symbol:
                    print('Selling ', target_currency)
                    amount = user.current_currency_balance
                    try:
                        order = user_exchange.create_order(user.pair, 'market', 'sell', amount)
                        if order:
                            print(order)
                            price = user_exchange.fetch_ticker(user.pair)
                            new_order = Orders()
                            new_order.order_id = order['id']
                            new_order.market = order['symbol']
                            new_order.side = order['side']
                            new_order.size = order['info']['size']
                            new_order.filled = order['filled']
                            new_order.filled_price = price['close']
                            new_order.fee = round(order['fee']['cost'], 2)
                            new_order.status = order['status']
                            new_order.amount = order['cost']
                            new_order.user_strategy_pair = user
                            new_order.user = user.user
                            new_order.save()
                    except Exception as e:
                        print("An exception occurred: ", e)
                        # send_email.send_daily_email(None, type(e))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return

def update_orders():
    open_orders = Orders.objects.filter(status='open')
    try:
        print('Updating orders')
        for open_order in open_orders:
            user_strategy_pair = User_Strategy_Pair.objects.filter(id=open_order.user_strategy_pair_id).first()
            user_exchange_account = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=user_strategy_pair.user_exchange_account_id).first()
            exchange = Exchange.objects.filter(exchange_id=user_exchange_account.exchange_id).first()
            user_exchange = helpers.get_exchange(exchange.name, user_exchange_account.api_key, user_exchange_account.api_secret, user_exchange_account.sub_account_name, user_exchange_account.api_password)
            completed_order = user_exchange.fetch_order(open_order.order_id)
            open_order.filled = completed_order['filled']
            open_order.fee = round(completed_order['fee']['cost'], 2)
            open_order.status = completed_order['status']
            print(completed_order)
            split = user_strategy_pair.pair.index('/')
            first_symbol = user_strategy_pair.pair[:split]
            second_symbol = user_strategy_pair.pair[split+1:]
            if open_order.side == 'buy':
                user_strategy_pair.current_currency = first_symbol
                user_strategy_pair.current_currency_balance = completed_order['amount']
                open_order.amount = completed_order['amount']
            if open_order.side == 'sell':
                user_strategy_pair.current_currency = second_symbol
                user_strategy_pair.current_currency_balance = completed_order['cost'] - round(completed_order['fee']['cost'], 2)
                open_order.amount = completed_order['cost']
            open_order.save()
            user_strategy_pair.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return
        