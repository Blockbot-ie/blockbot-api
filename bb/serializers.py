from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, JsonResponse
from bb.models import User, Strategy, Exchange, User_Exchange_Account
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
        fields = ('api_key', 'api_secret', 'exchange', 'user', )

    def validate(self, data):
        print(data)
        exchange_object = Exchange.objects.filter(exchange_id=data['exchange'].exchange_id).first()
        exchange_class = getattr(ccxt, exchange_object.name)
        exchange = exchange_class({
            'apiKey': data['api_key'],
            'secret': data['api_secret'],
            'timeout': 30000,
            'enableRateLimit': True
        })
        try:
            exchange.fetch_balance()
            if exchange:
                connect_exchange = User_Exchange_Account()
                connect_exchange.api_key = data['api_key']
                connect_exchange.api_secret = data['api_secret']
                connect_exchange.user = data['user'].user_id
                connect_exchange.exchange = exchange_object
                return connect_exchange
        except AttributeError as error:
            print(error)
            return JsonResponse(error.message_dict, safe=False)
        raise serializers.ValidationError("Incorrect Credentials")
        

        