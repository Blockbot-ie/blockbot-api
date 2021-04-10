from django.core.management.base import BaseCommand, CommandError
from trading_scripts.jobs import update_user_strategy_pair_balances
from bb.models import Strategy
from trading_scripts.services import helpers
import sys, os

class Command(BaseCommand):
    help = 'Saving users strategy pair balances'
    def handle(self, *args, **options):
        try:
            update_user_strategy_pair_balances.main()
            self.stdout.write(self.style.SUCCESS('All strategy balances updated'))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return
        return

