from django.core.management.base import BaseCommand, CommandError
from trading_scripts.strategies import strategy_0
from bb.models import Strategy
import sys, os

class Command(BaseCommand):
    help = 'Algorithm to buy and sell based on 20 Week Moving Average'
    def handle(self, *args, **options):
        try:
            strategy = Strategy.objects.filter(strategy_id='4a5ac44c-bec2-4128-a9fa-f9a744c1d99d').first()
            strategy_0.strategy_0_main(strategy)
            strategy_0.strategy_0_buy_or_sell(strategy)
            strategy_0.update_orders()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return

        self.stdout.write(self.style.SUCCESS('All suggested scripts updated'))
        return

