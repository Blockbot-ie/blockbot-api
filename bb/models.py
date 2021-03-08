import uuid
from django.db import models 
from django.db.models import Model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class Meta:
        db_table = 'bb_user'
class Strategy(models.Model):
    strategy_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Strategy Name'), max_length=150, blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    created_on = models.DateTimeField(_('created_on'), default=timezone.now)

class Exchange(models.Model):
    exchange_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Exchange Name'), max_length=150, blank=True)
    display_name = models.CharField(_('Display Name'), max_length=150, blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    created_on = models.DateTimeField(_('created_on'), default=timezone.now)
    
    
class User_Exchange_Account(models.Model):
    user_exchange_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    strategy = models.ForeignKey(Strategy, null=True, on_delete=models.SET_NULL)
    api_key = encrypt(models.CharField(_('API Key'), max_length=255, blank=True))
    api_secret = encrypt(models.CharField(_('API Secret'), max_length=255, blank=True))
    api_password = encrypt(models.CharField(_('API Password'), max_length=255, blank=True))
    sub_account_name = models.CharField(_('Sub-account Name'), max_length=255, null=True, blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    modified_on = models.DateTimeField(_('modified_on'), default=timezone.now)
    created_on = models.DateTimeField(_('created_on'), default=timezone.now)

# class User_Strategy_Pair(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_strategy_account = models.ForeignKey(User_Strategy_Account, null=True, on_delete=models.SET_NULL)
#     pair = models.CharField(_('Pair'), max_length=50, blank=True)
#     initial_first_symbol_balance = models.FloatField(_('Initial First Symbol Balance'), null=True, blank=True)
#     initial_second_symbol_balance = models.FloatField(_('Initial First Symbol Balance'), null=True, blank=True)
#     current_currency = models.CharField(_('Current Currency'), max_length=50, blank=True)
#     current_currency_balance = models.FloatField(_('Current Currency Balance'), null=True, blank=True)
#     is_active = models.BooleanField(
#         _('active'),
#         default=True,
#     )
#     modified_on = models.DateTimeField(_('modified_on'), default=timezone.now)
#     created_on = models.DateTimeField(_('created_on'), default=timezone.now)

# class Orders(models.Model):
#     order_id = models.IntegerField(primary_key=True, editable=False)
#     exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
#     pair = models.CharField(_('Pair'), max_length=50, blank=True)
#     order_type = models.CharField(_('Order Type'), max_length=50, blank=True)
#     currency_price = models.IntegerField(_('Currency Price'), default=0)
#     order_cost = models.IntegerField(_('Order Cost'), default=0)
#     order_status = models.CharField(_('Order Status'), max_length=50, blank=True)
#     order_side = models.CharField(_('Order Side'), max_length=50, blank=True)
#     modified_on = models.DateTimeField(_('modified_on'), default=timezone.now)
#     created_on = models.DateTimeField(_('created_on'), default=timezone.now)
#     user_strategy_account = models.ForeignKey(User_Strategy_Account, null=True, on_delete=models.SET_NULL)

class Strategy_Supported_Pairs(models.Model):
    pair_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.ForeignKey(Strategy, null=True, on_delete=models.SET_NULL)
    pair = models.CharField(_('Pair'), max_length=50, blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    created_on = models.DateTimeField(_('created_on'), default=timezone.now)

class Strategies_Suggested(models.Model):
    start_time_utc = models.DateTimeField(_('start_time_utc'), null=False)
    pair = models.ForeignKey(Strategy_Supported_Pairs, null=True, on_delete=models.SET_NULL)
    target_currency = models.CharField(_('Target Currency'), max_length=50, blank=True)
    tick = models.DateTimeField(_('Tick'), null=True, default=timezone.now)
