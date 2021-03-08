from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, JsonResponse
from bb.models import User, Strategy, Exchange, User_Exchange_Account, User_Strategy_Pair, Strategy_Supported_Pairs
import ccxt

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        return user

# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
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
    class Meta:
        model = User_Exchange_Account
        fields = ('name', 'api_key', 'api_secret', 'exchange', 'user', )

class ConnectStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Strategy_Pair
        fields = ('strategy', 'user_exchange_account', 'pair', 'initial_first_symbol_balance', 'initial_second_symbol_balance', 'current_currency', 'current_currency_balance',)
        
        
class StrategySupportedPairsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy_Supported_Pairs
        fields = ('strategy', 'pair')