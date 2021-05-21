from django import db
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from trading_scripts.strategies import strategies
from bb.models import Strategy, Orders
from trading_scripts.services import helpers
import sys, os
from multiprocessing import Pool
from functools import partial
db.connections.close_all()

class Command(BaseCommand):
    help = 'Algorithm to buy and sell based on 20 Week Moving Average'
    def handle(self, *args, **options):
        try:
            twenty_ten_strategy = Strategy.objects.filter(strategy_id='3c82058e-8007-4c8d-8ff5-3561f3870653').first()
            strategies.twenty_ten_MA(twenty_ten_strategy)
            multi_ma_strategy = Strategy.objects.filter(strategy_id='3c6bd390-7e32-426b-be28-54e9e430b223').first()
            strategies.multi_ma(multi_ma_strategy)
            eth_5_ema = Strategy.objects.filter(strategy_id='c2e1a3c4-f39e-4bdf-8094-16e5336f354a').first()
            strategies.eth_5_EMA(eth_5_ema)

            pairs = helpers.buy_or_sell()
            func = partial(helpers.run_buy_or_sell_process, pairs[0])
            a_pool = Pool(processes=4)
            a_pool.map(func, pairs[1])

            open_orders = Orders.objects.filter(Q(status='open')|Q(status='new'))
            print('Updating orders')
            a_pool = Pool(processes=4)
            a_pool.map(helpers.run_update_order_process, open_orders) 
            helpers.update_orders()
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return

        self.stdout.write(self.style.SUCCESS('All suggested scripts updated'))
        return

