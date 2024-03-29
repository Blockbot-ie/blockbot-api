import django
from django import db
django.setup()
import datetime as dt
from django.utils import timezone
import ccxt
from bb.models import User, Strategies_Suggested, Strategy_Supported_Pairs, Pairs, User_Strategy_Pair, User_Exchange_Account, Exchange, Orders
import os
import os.path
import sys
from trading_scripts.services import emails
from django.db.models import Q

def get_target_currencies():
    print('Getting target currencies')
    strategy_supported_pairs = Strategy_Supported_Pairs.objects.filter(is_active=True)
    target_currencies = []
    now = dt.datetime.now(tz=timezone.utc)
    earlier = now - dt.timedelta(minutes=2)
    for pair in strategy_supported_pairs:   
        data = {}
        target_currency = Strategies_Suggested.objects.filter(pair_id=pair.strategy_pair_id, tick__gte=earlier).first()
        symbol = Pairs.objects.filter(pair_id=pair.pair_id).first()
        data['strategy'] = pair.strategy_id
        data['pair'] = symbol.symbol
        data['target_currency'] = target_currency.target_currency
        target_currencies.append(data)
    return target_currencies

def get_exchange(exchange, api_key, api_secret, subaccount, password):
    print('Getting ccxt exchange')
    try:
        if exchange == 'ftx' and subaccount != '':
            exchange = getattr(ccxt, exchange)({
                'apiKey': api_key,
                'secret': api_secret,
                'timeout': 10000,
                'enableRateLimit': True,
                'headers': {'FTX-SUBACCOUNT': subaccount},
            })
        if exchange == 'coinbasepro' and password != '':
            exchange = getattr(ccxt, exchange)({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'timeout': 10000,
                    'enableRateLimit': True,
                    'password': password
                })
        else:
            exchange = getattr(ccxt, exchange)({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'timeout': 10000,
                    'enableRateLimit': True
                })
    except Exception as e:
        print(e)
    return exchange

def buy_or_sell():
    """
    Function to buy and sell
    output:
    """
    try:
        print('Starting buy and sell script')
        user_strategy_pairs = User_Strategy_Pair.objects.filter(is_active=True)
        target_currencies = get_target_currencies()
        return target_currencies, user_strategy_pairs       

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return

def run_buy_or_sell_process(target_currencies, user):
    try:
        user_exchange_account = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=user.user_exchange_account_id).first()
        exchange = Exchange.objects.filter(exchange_id=user_exchange_account.exchange_id).first()
        user_exchange = get_exchange(exchange.name, user_exchange_account.api_key, user_exchange_account.api_secret, user_exchange_account.sub_account_name, user_exchange_account.api_password)
        target_currency = [x['target_currency'] for x in target_currencies if x['pair'] == user.pair and user.strategy_id][0]
        split = user.pair.index('/')
        first_symbol = user.pair[:split]
        second_symbol = user.pair[split+1:]
        
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
                        new_order.size_symbol = second_symbol
                        new_order.filled_price = price['close']
                        new_order.user_strategy_pair = user
                        new_order.user = user.user
                        if user_exchange.id == 'binance':
                            new_order = binance_buy_order(new_order, order, user_exchange)
                        else:
                            new_order = coinbasepro_buy_order(new_order, order)
                        new_order.save()

                except Exception as e:
                    print("An exception occurred: ", e)
                    user.no_of_failed_attempts += 1
                    if user.no_of_failed_attempts >= 5:
                        user.is_active = False
                    user.save()
                    user_info = User.objects.get(user_id=user.user_id)
                    emails.send_order_error_email(user_info, e.args, user.no_of_failed_attempts)
            
            elif target_currency == second_symbol:
                print('Selling ', target_currency)
                amount = user.current_currency_balance
                try:
                    order = user_exchange.create_order(user.pair, 'market', 'sell', amount)
                    if order:
                        price = user_exchange.fetch_ticker(user.pair)
                        new_order = Orders()
                        new_order.size_symbol = first_symbol
                        new_order.filled_price = price['close']
                        new_order.user_strategy_pair = user
                        new_order.user = user.user
                        if user_exchange.id == 'binance':
                            new_order = binance_sell_order(new_order, order, user_exchange)
                        else:
                            new_order = coinbasepro_sell_order(new_order, order)
                        new_order.save()
                except Exception as e:
                    print("An exception occurred: ", e)
                    user.no_of_failed_attempts += 1
                    if user.no_of_failed_attempts >= 5:
                        user.is_active = False
                    user.save()
                    user_info = User.objects.get(user_id=user.user_id)
                    emails.send_order_error_email(user_info, e.args, user.no_of_failed_attempts)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return


def run_update_order_process(open_order):
    try:
        user_strategy_pair = User_Strategy_Pair.objects.filter(id=open_order.user_strategy_pair_id).first()
        user_exchange_account = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=user_strategy_pair.user_exchange_account_id).first()
        exchange = Exchange.objects.filter(exchange_id=user_exchange_account.exchange_id).first()
        print("Updating order for pair {0} with order id {1}".format(user_strategy_pair.id, open_order.order_id))
        user_exchange = get_exchange(exchange.name, user_exchange_account.api_key, user_exchange_account.api_secret, user_exchange_account.sub_account_name, user_exchange_account.api_password)
        completed_order = user_exchange.fetch_order(open_order.order_id, open_order.market)
        open_order.filled = completed_order['filled']
        open_order.status = completed_order['status']
        if user_exchange.id != 'binance':
            open_order.fee = round(completed_order['fee']['cost'], 2)
        split = user_strategy_pair.pair.index('/')
        first_symbol = user_strategy_pair.pair[:split]
        second_symbol = user_strategy_pair.pair[split+1:]
        if open_order.side == 'buy':
            user_strategy_pair.current_currency = first_symbol
            user_strategy_pair.current_currency_balance = completed_order['amount']
            open_order.amount = completed_order['amount']
        if open_order.side == 'sell':
            user_strategy_pair.current_currency = second_symbol
            user_strategy_pair.current_currency_balance = completed_order['cost'] - open_order.fee
            open_order.amount = completed_order['cost']
        open_order.save()
        print("Order {0} updated successfully".format(open_order.order_id))
        user_strategy_pair.no_of_failed_attempts = 0
        user_strategy_pair.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return

def binance_buy_order(new_order, order, user_exchange):
    new_order.order_id = order['id']
    new_order.market = order['symbol']
    new_order.side = order['side']
    new_order.size = order['cost']
    new_order.filled = order['filled']
    new_order.status = 'open'
    new_order.amount = order['amount']
    new_order.price = order['price']
    if order['fee']['currency'] != 'USDT':
        fee_price = user_exchange.fetch_ticker(order['fee']['currency'] + '/USDT')
        new_order.fee = order['fee']['cost'] * fee_price['close']
    else:
        new_order.fee = order['fee']['cost']
    return new_order

def binance_sell_order(new_order, order, user_exchange):
    new_order.order_id = order['id']
    new_order.market = order['symbol']
    new_order.side = order['side']
    new_order.size = order['amount']
    new_order.filled = order['filled']
    new_order.status = 'open'
    new_order.amount = order['cost']
    new_order.price = order['price']
    if order['fee']['currency'] != 'USDT':
        fee_price = user_exchange.fetch_ticker(order['fee']['currency'] + '/USDT')
        new_order.fee = order['fee']['cost'] * fee_price['close']
    else:
        new_order.fee = order['fee']['cost']
    return new_order

def coinbasepro_buy_order(new_order, order):
    new_order.order_id = order['id']
    new_order.market = order['symbol']
    new_order.side = order['side']
    new_order.size = order['info']['specified_funds']
    new_order.filled = order['filled']
    new_order.fee = round(order['fee']['cost'], 2)
    new_order.status = order['status']
    new_order.amount = order['amount']
    return new_order

def coinbasepro_sell_order(new_order, order):
    new_order.order_id = order['id']
    new_order.market = order['symbol']
    new_order.side = order['side']
    new_order.size = order['info']['size']
    new_order.filled = order['filled']
    new_order.fee = round(order['fee']['cost'], 2)
    new_order.status = order['status']
    new_order.amount = order['cost']
    return new_order