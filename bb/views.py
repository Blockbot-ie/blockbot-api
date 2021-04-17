from rest_framework import permissions, status, generics, mixins
from rest_framework.response import Response
from django.http import JsonResponse
import json
from django.db import IntegrityError
from django.db.models import Sum
import ccxt
from .models import User, Strategy, Exchange, User_Exchange_Account, User_Strategy_Pair, Strategy_Supported_Pairs, Pairs, Orders, User_Strategy_Pair_Daily_Balance, Exchange_Supported_Pairs
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, StrategySerializer, ExchangeSerializer, ConnectExchangeSerializer, ConnectStrategySerializer, StrategySupportedPairsSerializer, OrdersSerializer, GetConnectedExchangesSerializer, GetConnectedStrategiesSerializer
import datetime as dt
import time
from trading_scripts.services.helpers import send_bug_email
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework_simplejwt.backends import TokenBackend


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://127.0.0.1:3000/api/dj-rest-auth/google/callback/"

# Register API
class RegisterAPI(generics.GenericAPIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """
    serializer_class = RegisterSerializer

    # def post(self, request, *args, **kwargs):
    #     try:
    #         serializer = self.get_serializer(data=request.data)
    #         if serializer.is_valid():
    #             user = serializer.save()
    #             new_user = User.objects.filter(email=user.email).first()
    #             new_user.first_name = request.data["first_name"]
    #             new_user.last_name = request.data["last_name"]
    #             new_user.last_login = dt.datetime.utcnow()
    #             new_user.save()
    #             return Response({
    #                 "user": UserSerializer(user, context=self.get_serializer_context()).data,
    #                 "token": AuthToken.objects.create(user)[1]
    #                 })
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         print(e)
    #         return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

# Login API
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.validated_data
    #     _, token = AuthToken.objects.create(user)
    #     return Response({
    #         "user": UserSerializer(user, context=self.get_serializer_context()).data,
    #         "token": token
    #     })

# Get User API
class UserAPI(generics.RetrieveAPIView):
    """
    Determine the current user by their token, and return their data
    """
    permission_classes = [
    permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class DashBoardData(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user_pairs = User_Strategy_Pair.objects.filter(user_id=self.request.user.user_id, is_active=True) 
        
        inc_or_dec_vs_hodl = []
        balances = 0.0
        for pair in user_pairs:
            strategy = Strategy.objects.filter(is_active=True, strategy_id=pair.strategy_id).first()
            user_exchange_account = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=pair.user_exchange_account_id).first()
            if user_exchange_account:
                exchange_object = Exchange.objects.filter(exchange_id=user_exchange_account.exchange_id).first()
                exchange = getattr (ccxt, exchange_object.name) ()
                price = exchange.fetch_ticker(pair.pair)
                split = pair.pair.index('/')
                first_symbol = pair.pair[:split]
                second_symbol = pair.pair[split+1:]
                current_asset_value = pair.current_currency_balance
                balance = pair.current_currency_balance
                if pair.current_currency == second_symbol:
                    current_asset_value = pair.current_currency_balance/price['close']
                else:
                    balance = pair.current_currency_balance * price['close']
                balances += balance
                diff = current_asset_value - pair.initial_first_symbol_balance
                inc_or_dec = (diff/pair.initial_first_symbol_balance) * 100
                inc_or_dec_object_to_add = {
                    'exchange_account': pair.user_exchange_account_id,
                    'exchange_account_name': user_exchange_account.name,
                    'strategy_id': pair.strategy_id,
                    'strategy_name': strategy.name,
                    'pair': pair.pair,
                    'inc_or_dec': inc_or_dec,
                    'balance': balance
                }
                inc_or_dec_vs_hodl.append(inc_or_dec_object_to_add)
                    
        active_strategies = user_pairs.count()
        content = {
            'balance': balances,
            'active_strategies': active_strategies,
            'inc_or_dec_vs_hodl': inc_or_dec_vs_hodl
        }
        return Response(content, status=status.HTTP_200_OK)


class StrategyList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class ExchangeList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):

    permission_classes = (permissions.AllowAny, )
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class GetConnectedExchanges(mixins.CreateModelMixin,
                            generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = GetConnectedExchangesSerializer
    
    def get(self, request, *args, **kwargs):
        queryset = User_Exchange_Account.objects.filter(user_id=self.request.user.user_id)
        content = []
        user_id = self.request.user.user_id
        if user_id is not None:
            for exchange in queryset:
                user_strategy_pairs = User_Strategy_Pair.objects.filter(user_exchange_account_id=exchange.user_exchange_account_id)
                count = user_strategy_pairs.count()
                serializer = self.get_serializer(exchange)
                ccxt_exchange = connect_to_users_exchange(exchange)
                available_amounts = available_balances(exchange, ccxt_exchange)
                data = {
                    "exchange": serializer.data,
                    "strategy_count": count,
                    "available_balances": available_amounts
                }
                content.append(data)
            return Response(content, status=status.HTTP_200_OK)
        return queryset.none()

class ConnectExchange(mixins.CreateModelMixin,
                    generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ConnectExchangeSerializer

    def post(self, request, *args, **kwargs):
        exchange_object = Exchange.objects.filter(exchange_id=request.data['exchange']).first()
        try:
            exchange_id = exchange_object.name
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class({
                'apiKey': request.data['api_key'],
                'secret': request.data['api_secret'],
                'password': request.data['api_password'],
                'timeout': 30000,
                'enableRateLimit': True,
            })
            account_id = exchange.fetch_balance()
            account_id = account_id["info"][0]['profile_id']
            
        except Exception as error:
            print(error)
            content = {'Error': str(error)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        user_account_with_current_exchange = User_Exchange_Account.objects.filter(exchange_id=exchange_object.exchange_id, user_id=self.request.user.user_id)
        request.data['name'] = exchange_object.display_name + " " + str(user_account_with_current_exchange.count() + 1)
        request.data['user_exchange_account_id'] = account_id
        request.data['user'] = self.request.user.user_id
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as err:
            content = {'Error': str(err)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            content = {'Error': str(error)}
            print(error)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

class GetConnectedStrategies(mixins.CreateModelMixin,
                            generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = GetConnectedStrategiesSerializer
    
    def get_queryset(self):
        queryset = User_Strategy_Pair.objects.all()
        user_id = self.request.user.user_id
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
            return queryset
        return queryset.none()

class ConnectStrategy(mixins.CreateModelMixin,
                    generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ConnectStrategySerializer

    def post(self, request, *args, **kwargs):
        print(self.request.user.user_id)
        user_exchange_account = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=request.data['user_exchange_account']).first()
        try:
            if user_exchange_account:
                exchange_id = 'coinbasepro'
                exchange_class = getattr(ccxt, exchange_id)
                exchange = exchange_class({
                    'apiKey': user_exchange_account.api_key,
                    'secret': user_exchange_account.api_secret,
                    'password': user_exchange_account.api_password,
                    'timeout': 30000,
                    'enableRateLimit': True,
                })
                balance = exchange.fetch_balance()
                price = exchange.fetch_ticker(request.data['pair'])
                current_balance = [x for x in balance["info"] if x['currency'] == request.data['current_currency']]
                current_balance = current_balance[0]['balance']
                user_strategies_with_current_currency = User_Strategy_Pair.objects.filter(is_active=True, user_exchange_account_id=request.data['user_exchange_account'], current_currency=request.data['current_currency'])
                balance_taken_by_strategies = user_strategies_with_current_currency.aggregate(Sum('current_currency_balance'))
                if balance_taken_by_strategies['current_currency_balance__sum'] is not None:
                    balance_available = float(current_balance) - balance_taken_by_strategies['current_currency_balance__sum']
                else:
                    balance_available = float(current_balance)
                if balance_available < request.data['current_currency_balance']:
                    amount_required = request.data['current_currency_balance'] - balance_available
                    content = {'Error': "Insufficient Funds. Please fund your account with {0} {1}".format(amount_required, request.data['current_currency'])}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            content = {'Error': str(error)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        request.data['user'] = self.request.user.user_id
        if request.data['initial_first_symbol_balance'] is None or request.data['initial_first_symbol_balance'] == 0:
            request.data['initial_first_symbol_balance'] = request.data['initial_second_symbol_balance']/price['close']
        else:
            request.data['initial_second_symbol_balance'] = price['close'] * request.data['initial_first_symbol_balance']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.filter(user_id=self.request.user.user_id).first()
        user.is_connected = True
        user.save()
        try:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error:
            content = {'Error': str(error)}
            print(error)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

class StrategyPairs(mixins.CreateModelMixin,
                    generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = StrategySupportedPairsSerializer

    def get(self, request, *args, **kwargs):
        strategy_pairs = Strategy_Supported_Pairs.objects.filter(is_active=True)
        content = []
        for pair in strategy_pairs:
            pair_entity = Pairs.objects.filter(pair_id=pair.pair_id).first()
            exchanges = Exchange_Supported_Pairs.objects.filter(pair_id=pair_entity.pair_id).values('exchange_id')
            pair_object = {
                "strategy_id": pair.strategy_id,
                "symbol": pair_entity.symbol,
                "ticker_1":  pair_entity.ticker_1,
                "ticker_2": pair_entity.ticker_2,
                "ticker_1_min_value": pair_entity.ticker_1_min_value,
                "ticker_2_min_value": pair_entity.ticker_2_min_value,
                "supported_exchanges": exchanges
            }
            content.append(pair_object)            
        return Response(content, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.user_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            content = {'Success': 'Strategy connection successful'}
            return Response(content, status=status.HTTP_201_CREATED)
        except Exception as error:
            content = {'Error': str(error)}
            print(error)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

class OrdersList(mixins.CreateModelMixin,
                    generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = OrdersSerializer
    
    def get_queryset(self):
        user_id = self.request.user.user_id
        if user_id is not None:
            queryset = Orders.objects.filter(user=user_id).order_by('-created_on')
            return queryset
        return queryset.none()
    
class BugReport(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        data = request.data
        send_bug_email(data["type"], data["area"], data["issue"], self.request.user.email)

        content = {'Success': 'Bug report submission successful'}
        return Response(content, status=status.HTTP_201_CREATED)

class TopUpStrategy(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user_strategy_pair = User_Strategy_Pair.objects.filter(is_active=True, id=request.data['strategy_pair_id']).first()
        user_exchange_account = User_Exchange_Account.objects.filter(is_active=True, user_exchange_account_id=user_strategy_pair.user_exchange_account_id).first()
        exchange = connect_to_users_exchange(user_exchange_account)
        split = user_strategy_pair.pair.index('/')
        first_symbol = user_strategy_pair.pair[:split]
        second_symbol = user_strategy_pair.pair[split+1:]
        if user_strategy_pair.current_currency == request.data['currency']:
            # check account to see if there is enough of the current currency
            enough = check_account_for_available_balances(user_exchange_account, exchange, request.data['currency'], request.data['amount'])
            if enough == True:
                user_strategy_pair.current_currency_balance += request.data['amount']
                if user_strategy_pair.current_currency == first_symbol:
                    user_strategy_pair.initial_first_symbol_balance += request.data['amount']
                else:
                    user_strategy_pair.initial_second_symbol_balance += request.data['amount']
            else:
                # not enough balance in account
                return enough
        else:
            # check account to see if there is enough of the selected currency
            # if there is then buy or sell into the current currency
            enough = check_account_for_available_balances(user_exchange_account, exchange, request.data['currency'], request.data['amount'])
            if enough:
                if request.data['currency'] == second_symbol:
                    print('Buying ', first_symbol)
                    amount = 1
                    price = request.data['amount']
                    try:
                        order = exchange.create_order(user_strategy_pair.pair, 'market', 'buy', amount, price)
                        if order:
                            price = exchange.fetch_ticker(user_strategy_pair.pair)
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
                            new_order.user_strategy_pair = user_strategy_pair
                            new_order.user = self.request.user
                            new_order.save()
                            update_order(order['id'], exchange, user_strategy_pair)
                            user_strategy_pair.initial_second_symbol_balance += request.data['amount']
                    except Exception as e:
                        print("An exception occurred: ", e)
                else:
                    print('Selling ', second_symbol)
                    amount = request.data['amount']
                    try:
                        order = exchange.create_order(user_strategy_pair.pair, 'market', 'sell', amount)
                        if order:
                            
                            price = exchange.fetch_ticker(user_strategy_pair.pair)
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
                            new_order.user_strategy_pair = user_strategy_pair
                            new_order.user = self.request.user
                            new_order.save()
                            update_order(order['id'], exchange, user_strategy_pair)
                            user_strategy_pair.initial_first_symbol_balance += request.data['amount']
                    except Exception as e:
                        print("An exception occurred: ", e)
                        # send_email.send_daily_email(None, type(e))
            else:
                return enough
        user_strategy_pair.save()
        daily_balance = User_Strategy_Pair_Daily_Balance.objects.filter(user_strategy_pair=user_strategy_pair.id, created_on=dt.date.today()).first()
        daily_balance.is_top_up = True
        daily_balance.save()
        content = {'Success': 'Topped up successfully'}
        return Response(content, status=status.HTTP_201_CREATED)

class GetDailyBalances(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = self.request.user.user_id
        content = []
        for user_strategy_pair in User_Strategy_Pair.objects.filter(user_id=user):
            data = {}
            strategy_balances = User_Strategy_Pair_Daily_Balance.objects.filter(user_strategy_pair=user_strategy_pair.id).order_by('created_on')
            if strategy_balances is not None:
                data["strategy_id"] = user_strategy_pair.id
                sub_data = []
                for balance in strategy_balances:
                    object_to_append = {
                        "date": balance.created_on,
                        "hodl_value": balance.hodl_value,
                        "strategy_value": balance.strategy_value
                        }
                    sub_data.append(object_to_append)
                data["data"] = sub_data
                content.append(data)
                
        return Response(content, status=status.HTTP_200_OK)


def connect_to_users_exchange(user_exchange_account):
    exchange_name = Exchange.objects.filter(exchange_id=user_exchange_account.exchange_id).first()
    try:
        if user_exchange_account:
            exchange_id = exchange_name.name
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class({
                'apiKey': user_exchange_account.api_key,
                'secret': user_exchange_account.api_secret,
                'password': user_exchange_account.api_password,
                'timeout': 30000,
                'enableRateLimit': True,
            })
    except Exception as error:
        content = {'Error': str(error)}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    return exchange


def check_account_for_available_balances(user_exchange_account, exchange, currency, amount):    
    balance = exchange.fetch_balance()
    current_balance = [x for x in balance["info"] if x['currency'] == currency]
    current_balance = current_balance[0]['balance']
    user_strategies_with_current_currency = User_Strategy_Pair.objects.filter(is_active=True, user_exchange_account_id=user_exchange_account.user_exchange_account_id, current_currency=currency)
    balance_taken_by_strategies = user_strategies_with_current_currency.aggregate(Sum('current_currency_balance'))
    if balance_taken_by_strategies['current_currency_balance__sum'] is not None:
        balance_available = float(current_balance) - balance_taken_by_strategies['current_currency_balance__sum']
    else:
        balance_available = float(current_balance)
    if balance_available < amount:
        amount_required = amount - balance_available
        content = {'Error': "Insufficient Funds. Please fund your account with {0} {1}".format(amount_required, currency)}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    return True

def available_balances(user_exchange_account, exchange):
    balance = exchange.fetch_balance()
    available_amounts = {}
    for i in ['USDC', 'BTC', 'ETH']:
        new_balance = [x for x in balance["info"] if x['currency'] == i]
        user_strategies_with_current_currency = User_Strategy_Pair.objects.filter(is_active=True, user_exchange_account_id=user_exchange_account.user_exchange_account_id, current_currency=i)
        balance_taken_by_strategies = user_strategies_with_current_currency.aggregate(Sum('current_currency_balance'))
        if balance_taken_by_strategies['current_currency_balance__sum'] is not None:
            available_amounts[i] = float(new_balance[0]['balance']) - balance_taken_by_strategies['current_currency_balance__sum']
        else:
            available_amounts[i] = float(new_balance[0]['balance'])

    return available_amounts
    
def update_order(order_id, exchange, user_strategy_pair):
    time.sleep(1)
    new_order = Orders.objects.filter(order_id=order_id).first()
    completed_order = exchange.fetch_order(order_id)
    new_order.filled = completed_order['filled']
    new_order.fee = round(completed_order['fee']['cost'], 2)
    new_order.status = completed_order['status']
    split = user_strategy_pair.pair.index('/')
    first_symbol = user_strategy_pair.pair[:split]
    second_symbol = user_strategy_pair.pair[split+1:]
    if new_order.side == 'buy':
        user_strategy_pair.current_currency = first_symbol
        user_strategy_pair.current_currency_balance += completed_order['amount']
        user_strategy_pair.initial_first_symbol_balance += completed_order['amount']
        new_order.amount = completed_order['amount']
    if new_order.side == 'sell':
        user_strategy_pair.current_currency = second_symbol
        user_strategy_pair.current_currency_balance += completed_order['cost'] - round(completed_order['fee']['cost'], 2)
        user_strategy_pair.initial_second_symbol_balance += completed_order['cost'] - round(completed_order['fee']['cost'], 2)
        new_order.amount = completed_order['cost']
    new_order.save()
    user_strategy_pair.save()


        