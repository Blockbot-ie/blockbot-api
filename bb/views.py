from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework import permissions, status, generics, mixins
from rest_framework.response import Response
from knox.models import AuthToken
from .models import Strategy, Exchange
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, StrategySerializer, ExchangeSerializer

# Register API
class RegisterAPI(generics.GenericAPIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
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
        print(request)
        return self.list(request, *args, **kwargs)

class ExchangeList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):

    permission_classes = (permissions.AllowAny, )
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)