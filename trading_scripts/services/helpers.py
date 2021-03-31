import datetime as dt
from django.utils import timezone
import ccxt
from bb.models import Strategies_Suggested, Strategy_Supported_Pairs, Pairs, User_Strategy_Pair, User_Exchange_Account, Exchange, Orders
import os
import os.path
import ssl, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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



def send_bug_email(issue_type, area, issue, sender):
    print('Starting daily email job')
    try:
        html = """\
                <html>
                <body>
                    <h4>{0}</h4>
                    <h2>{1}</h2>
                    <p>{2}</p>                    
                </body>
                </html>
                """.format(issue_type, area, issue)
    
        port = 465
        gmail_password = 'ClingomintAMDG101'
        # Create a secure SSL context
        context = ssl.create_default_context()

        sender_email = sender
        receiver_email = "blockbotie@gmail.com"
        message = MIMEMultipart("alternative")
        message["Subject"] = issue_type
        message["From"] = sender_email

        part1 = MIMEText(html, "html")
        message.attach(part1)

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            print('Logging into email server')
            server.login(sender_email, gmail_password)
            print('Sending email')
            message["To"] = receiver_email
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
            print('Email sent to {0}'.format(receiver_email))
    except Exception as error:
        print("Error sending order emails ", error)

def buy_or_sell():
    """
    Function to buy and sell
    output:
    """
    try:
        print('Starting buy and sell script')
        target_currencies = get_target_currencies()
        user_strategy_pairs = User_Strategy_Pair.objects.filter(is_active=True)
        for user in user_strategy_pairs:
            user_exchange_account = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=user.user_exchange_account_id).first()
            exchange = Exchange.objects.filter(exchange_id=user_exchange_account.exchange_id).first()
            user_exchange = get_exchange(exchange.name, user_exchange_account.api_key, user_exchange_account.api_secret, user_exchange_account.sub_account_name, user_exchange_account.api_password)
            target_currency = [x['target_currency'] for x in target_currencies if x['pair'] == user.pair and user.strategy_id][0]
            
            split = user.pair.index('/')
            first_symbol = user.pair[:split]
            second_symbol = user.pair[split+1:]
            try:
                balances = user_exchange.fetch_balance()
            except Exception as e:
                print(e)
            
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
            user_exchange = get_exchange(exchange.name, user_exchange_account.api_key, user_exchange_account.api_secret, user_exchange_account.sub_account_name, user_exchange_account.api_password)
            completed_order = user_exchange.fetch_order(open_order.order_id)
            open_order.filled = completed_order['filled']
            open_order.fee = round(completed_order['fee']['cost'], 2)
            open_order.status = completed_order['status']
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
