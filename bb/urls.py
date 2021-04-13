from django.urls import path, include, re_path
from .views import RegisterAPI, LoginAPI, UserAPI, DashBoardData, StrategyList, ExchangeList, ConnectExchange, GetConnectedExchanges, ConnectStrategy, GetConnectedStrategies, StrategyPairs, OrdersList, BugReport, TopUpStrategy
from django.views.generic import TemplateView

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/register', RegisterAPI.as_view()),
    path('auth/login', LoginAPI.as_view()),
    path('auth/user', UserAPI.as_view()),
    
    path('dashboard-data', DashBoardData.as_view()),
    path('strategies/', StrategyList.as_view()),
    path('exchanges/', ExchangeList.as_view()),
    path('connect-exchange', ConnectExchange.as_view()),
    path('get-connected-exchanges', GetConnectedExchanges.as_view()),
    path('connect-strategies', ConnectStrategy.as_view()),
    path('get-connected-strategies', GetConnectedStrategies.as_view()),
    path('strategy_pairs', StrategyPairs.as_view()),
    path('orders', OrdersList.as_view()),
    path('submit-bug-report', BugReport.as_view()),
    path('top-up-strategy', TopUpStrategy.as_view())
    ]

urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]