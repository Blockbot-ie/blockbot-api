from django.core.management.base import BaseCommand, CommandError
from trading_scripts.strategies import strategies
from bb.models import Strategy
from trading_scripts.services import helpers
import sys, os

class Command(BaseCommand):
    help = 'Algorithm to buy and sell based on 20 Week Moving Average'
    def handle(self, *args, **options):
        try:
            # twenty_strategy = Strategy.objects.filter(strategy_id='4a5ac44c-bec2-4128-a9fa-f9a744c1d99d').first()
            # strategies.twenty_MA(twenty_strategy)
            twenty_ten_strategy = Strategy.objects.filter(strategy_id='3c82058e-8007-4c8d-8ff5-3561f3870653').first()
            strategies.twenty_ten_MA(twenty_ten_strategy)
            multi_ma_strategy = Strategy.objects.filter(strategy_id='3c6bd390-7e32-426b-be28-54e9e430b223').first()
            strategies.multi_ma(multi_ma_strategy)
            helpers.buy_or_sell()
            helpers.update_orders()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return

        self.stdout.write(self.style.SUCCESS('All suggested scripts updated'))
        return

