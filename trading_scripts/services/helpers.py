import datetime as dt
import ccxt
from bb.models import Strategies_Suggested, Strategy_Supported_Pairs, Pairs
import os
import os.path
import ssl, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_target_currencies(strategy):
    strategy_supported_pairs = Strategy_Supported_Pairs.objects.filter(strategy=strategy)
    target_currencies = []
    now = dt.datetime.utcnow()
    earlier = now - dt.timedelta(minutes=1)
    for pair in strategy_supported_pairs:
        data = {}
        target_currency = Strategies_Suggested.objects.filter(pair_id=pair.strategy_pair_id, tick__gte=earlier).first()
        symbol = Pairs.objects.filter(pair_id=pair.pair_id).first()
        data['pair'] = symbol.symbol
        data['target_currency'] = target_currency.target_currency
        target_currencies.append(data)

    return target_currencies

def get_exchange(exchange, api_key, api_secret, subaccount, password):
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