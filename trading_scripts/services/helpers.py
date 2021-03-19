import datetime as dt
import ccxt
from bb.models import Strategies_Suggested, Strategy_Supported_Pairs, Pairs

def get_target_currencies(strategy):
    strategy_supported_pairs = Strategy_Supported_Pairs.objects.filter(strategy=strategy)
    target_currencies = []
    now = dt.datetime.utcnow()
    earlier = now - dt.timedelta(minutes=2)
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
