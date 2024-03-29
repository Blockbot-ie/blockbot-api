from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, JsonResponse
from bb.models import User, Strategy, Exchange, User_Exchange_Account, User_Strategy_Pair, Strategy_Supported_Pairs, Orders
import ccxt
import datetime as dt
from dj_rest_auth.registration.serializers import RegisterSerializer

User._meta.get_field('email')._unique = True

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'email', 'is_connected')

# Register Serializer



class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', '')
        }

# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = User.objects.get(email=data["username"])
            if user.check_password(data["password"]):
                if user.is_active:
                    update_user = User.objects.filter(email=data["username"]).first()
                    update_user.last_login = dt.datetime.utcnow()
                    update_user.save()
                    return user
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=data["username"])
                if user.check_password(data["password"]):
                    if user.is_active:
                        update_user = User.objects.filter(username=data["username"]).first()
                        update_user.last_login = dt.datetime.utcnow()
                        update_user.save()
                        return user
            except User.DoesNotExist:
                raise serializers.ValidationError("Incorrect Credentials")

class StrategySerializer(serializers.ModelSerializer):

    class Meta:
        model = Strategy
        fields = ('strategy_id', 'name',)

class ExchangeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exchange
        fields = ('exchange_id', 'display_name', 'name', 'sign_up_url')

class ConnectExchangeSerializer(serializers.ModelSerializer):
    user_exchange_account_id = serializers.UUIDField()
    class Meta:
        model = User_Exchange_Account
        fields = ('user_exchange_account_id', 'name', 'api_key', 'api_secret', 'api_password', 'exchange', 'user')

    def validate(self, data):
        if data['user_exchange_account_id']:
            exchange_account = User_Exchange_Account.objects.filter(user_exchange_account_id=data['user_exchange_account_id']).first()
        if exchange_account:
            raise serializers.ValidationError("Exchange Account already Connected")
        else:
            return data

class GetConnectedExchangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Exchange_Account
        fields = ('user_exchange_account_id', 'name', 'exchange', )
        depth = 1

class ConnectStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Strategy_Pair
        fields = ('id', 'strategy', 'user_exchange_account', 'pair', 'initial_first_symbol_balance', 'initial_second_symbol_balance', 'current_currency', 'current_currency_balance', 'user')
    
    def validate(self, data):
        user_strategy_pair = User_Strategy_Pair.objects.filter(user_exchange_account_id=data['user_exchange_account'], pair=data['pair'], strategy=data['strategy']).first()
        if user_strategy_pair:
            raise serializers.ValidationError("Pair already in use. You can add more to your pair under strategies")
        else:
            return data

class GetConnectedStrategiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Strategy_Pair
        fields = ('id', 'strategy', 'user_exchange_account', 'pair', 'initial_first_symbol_balance', 'initial_second_symbol_balance', 'current_currency', 'current_currency_balance', 'is_active')
        depth = 1
        
        
class StrategySupportedPairsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy_Supported_Pairs
        fields = ('strategy', 'pair')

class OrdersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orders
        fields = ('order_id', 'side', 'status', 'market', 'size', 'filled', 'filled_price', 'fee', 'created_on')