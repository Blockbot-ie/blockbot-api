from django.urls import path, include
from .views import RegisterAPI, LoginAPI, UserAPI, DashBoardData, StrategyList, ExchangeList, ConnectExchange, ConnectStrategy, StrategyPairs, OrdersList
from knox import views as knox_views

urlpatterns = [
    path('auth', include('knox.urls')),
    path('auth/register', RegisterAPI.as_view()),
    path('auth/login', LoginAPI.as_view()),
    path('auth/user', UserAPI.as_view()),
    path('auth/logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('dashboard-data', DashBoardData.as_view()),
    path('strategies/', StrategyList.as_view()),
    path('exchanges/', ExchangeList.as_view()),
    path('connect-exchange', ConnectExchange.as_view()),
    path('connect-strategies', ConnectStrategy.as_view()),
    path('strategy_pairs', StrategyPairs.as_view()),
    path('orders', OrdersList.as_view())
    ]