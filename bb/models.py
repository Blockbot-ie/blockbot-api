import uuid
from django.db import models 
from django.db.models import Model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_connected = models.BooleanField(
        _('Connected'),
        default=False,
    )
    class Meta:
        db_table = 'bb_user'

class UserStory(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    stage = models.IntegerField(_('Story Stage'), default=1)

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

class Pairs(models.Model):
    pair_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(_('Symbol'), max_length=50, blank=True)
    ticker_1 = models.CharField(_('Ticker 1'), max_length=50, blank=True)
    ticker_2 = models.CharField(_('Ticker 2'), max_length=50, blank=True)
    ticker_1_min_value = models.FloatField(_('Ticker 1 Min Value'), null=True, blank=True)
    ticker_2_min_value = models.FloatField(_('Ticker 2 Min Value'), null=True, blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    created_on = models.DateTimeField(_('created_on'), default=timezone.now)
    
class User_Exchange_Account(models.Model):
    user_exchange_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Exchange Account Name'), max_length=255, blank=True, unique=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
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

class User_Strategy_Pair(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    strategy = models.ForeignKey(Strategy, null=True, on_delete=models.SET_NULL)
    user_exchange_account = models.ForeignKey(User_Exchange_Account, null=True, on_delete=models.SET_NULL)
    pair = models.CharField(_('Pair'), max_length=50, blank=True)
    initial_first_symbol_balance = models.FloatField(_('Initial First Symbol Balance'), null=True, blank=True)
    initial_second_symbol_balance = models.FloatField(_('Initial Second Symbol Balance'), null=True, blank=True)
    current_currency = models.CharField(_('Current Currency'), max_length=50, blank=True)
    current_currency_balance = models.FloatField(_('Current Currency Balance'), null=True, blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    modified_on = models.DateTimeField(_('modified_on'), default=timezone.now)
    created_on = models.DateTimeField(_('created_on'), default=timezone.now)

class Orders(models.Model):
    order_id = models.CharField(primary_key=True, max_length=50, editable=False)
    market = models.CharField(_('Market'), max_length=50, blank=True)
    side = models.CharField(_('Side'), max_length=50, blank=True)
    size = models.FloatField(_('Order Size'), default=0)
    filled = models.FloatField(_('Filled'), default=0)
    filled_price = models.FloatField(_('Filled Price'), default=0)
    fee = models.FloatField(_('Fee'), default=0)
    status = models.CharField(_('Status'), max_length=50, blank=True)
    amount = models.FloatField(_('Amount'), default=0)
    modified_on = models.DateTimeField(_('modified_on'), default=timezone.now)
    created_on = models.DateTimeField(_('created_on'), default=timezone.now)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    user_strategy_pair = models.ForeignKey(User_Strategy_Pair, null=True, on_delete=models.SET_NULL)

class Strategy_Supported_Pairs(models.Model):
    strategy_pair_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.ForeignKey(Strategy, null=True, on_delete=models.SET_NULL)
    pair = models.ForeignKey(Pairs, null=True, on_delete=models.SET_NULL)
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

class User_Strategy_Pair_Daily_Balance(models.Model):
    user_strategy_pair = models.ForeignKey(User_Strategy_Pair, null=True, on_delete=models.SET_NULL)
    price = models.FloatField(_('Pair Price'), default=0)
    hodl_value = models.FloatField(_('HODL Value'), default=0)
    strategy_value = models.FloatField(_('Strategy Value'), default=0)
    is_top_up = models.BooleanField(_('active'), default=False)
    created_on = models.DateField(_('created_on'), default=timezone.now)

class Exchange_Supported_Pairs(models.Model):
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    pair = models.ForeignKey(Pairs, null=True, on_delete=models.SET_NULL)