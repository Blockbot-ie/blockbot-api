from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, JsonResponse
from bb.models import User, Strategy, Exchange, User_Exchange_Account, User_Strategy_Pair, Strategy_Supported_Pairs
import ccxt
import datetime as dt

User._meta.get_field('email')._unique = True

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'email', 'is_connected')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'first_name', 'last_name', 'email', 'password', 'last_login')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.last_login = dt.datetime.now
        return user

# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            user.last_login = dt.datetime.now
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class StrategySerializer(serializers.ModelSerializer):

    class Meta:
        model = Strategy
        fields = ('strategy_id', 'name',)

class ExchangeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exchange
        fields = ('exchange_id', 'display_name',)

class ConnectExchangeSerializer(serializers.ModelSerializer):
    user_exchange_account_id = serializers.UUIDField()
    class Meta:
        model = User_Exchange_Account
        fields = ('user_exchange_account_id', 'name', 'api_key', 'api_secret', 'exchange', 'user', 'api_password',)

    def validate(self, data):
        exchange_account = User_Exchange_Account.objects.filter(user_exchange_account_id=data['user_exchange_account_id']).first()
        if exchange_account:
            raise serializers.ValidationError("Exchange Account already Connected")

class ConnectStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Strategy_Pair
        fields = ('strategy', 'user_exchange_account', 'pair', 'initial_first_symbol_balance', 'initial_second_symbol_balance', 'current_currency', 'current_currency_balance', 'user')
        
        
class StrategySupportedPairsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy_Supported_Pairs
        fields = ('strategy', 'pair')