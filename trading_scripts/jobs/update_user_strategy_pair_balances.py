from bb.models import User_Strategy_Pair, User_Strategy_Pair_Daily_Balance, User_Exchange_Account, Exchange, User
import ccxt

def main():
    print("Running Update Strategy Pairs Job")
    try:
        for user_pair in User_Strategy_Pair.objects.filter(is_active=True):
            user = User.objects.get(user_id=user_pair.user_id)
            print("Updating pair with id {}".format(user_pair.id))
            # init balance model
            daily_balance = User_Strategy_Pair_Daily_Balance()
            daily_balance.user_strategy_pair_id = user_pair.id
            daily_balance.user = user

            # get users exchange
            user_exchange = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=user_pair.user_exchange_account_id).first()
            exchange_info = Exchange.objects.filter(exchange_id=user_exchange.exchange_id).first()
            print("Getting data from {}".format(exchange_info.name))
            exchange = getattr (ccxt, exchange_info.name) ()
            # get current price
            price = exchange.fetch_ticker(user_pair.pair)

            if price:
                daily_balance.price = price['close']
            
            daily_balance.hodl_value = user_pair.initial_first_symbol_balance * price['close']
            
            # need to calculate balance of first symbol to find current value of pair
            split = user_pair.pair.index('/')
            first_symbol = user_pair.pair[:split]
            second_symbol = user_pair.pair[split+1:]

            if user_pair.current_currency == second_symbol:
                first_symbol_value = price['close'] / user_pair.current_currency_balance
                daily_balance.strategy_value = first_symbol_value * price['close']
            else:
                daily_balance.strategy_value = user_pair.current_currency_balance * price['close']
            print("Saving data")
            daily_balance.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return
