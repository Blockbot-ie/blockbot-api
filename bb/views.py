from rest_framework import permissions, status, generics, mixins
from rest_framework.response import Response
import ccxt
from knox.models import AuthToken
from .models import User, Strategy, Exchange, User_Exchange_Account, User_Strategy_Pair, Strategy_Supported_Pairs, Pairs
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, StrategySerializer, ExchangeSerializer, ConnectExchangeSerializer, ConnectStrategySerializer, StrategySupportedPairsSerializer
import datetime as dt

# Register API
class RegisterAPI(generics.GenericAPIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        try:
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.save()
        except Exception as error:
            print(error)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

# Login API
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        _, token = AuthToken.objects.create(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        })

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

class ConnectExchange(
                  mixins.CreateModelMixin,
                  generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ConnectExchangeSerializer
    
    def get_queryset(self):
        queryset = User_Exchange_Account.objects.all()
        user_id = self.request.user.user_id
        print(user_id)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
            return queryset
        return queryset.none()

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
            exchange.fetch_balance()
        except Exception as error:
            print(error)
            content = {'Error': str(error)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        request.data['user'] = self.request.user.user_id
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error:
            content = {'Error': str(error)}
            print(error)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

class ConnectStrategy(mixins.CreateModelMixin,
                    generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ConnectStrategySerializer

    def get_queryset(self):
        queryset = User_Strategy_Pair.objects.all()
        user_id = self.request.user.user_id
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
            return queryset
        return queryset.none()

    def post(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.user_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
            pair_object = {
                "strategy_id": pair.strategy_id,
                "symbol": pair_entity.symbol,
                "ticker_1":  pair_entity.ticker_1,
                "ticker_2": pair_entity.ticker_2,
                "ticker_1_min_value": pair_entity.ticker_1_min_value,
                "ticker_2_min_value": pair_entity.ticker_2_min_value
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

    
