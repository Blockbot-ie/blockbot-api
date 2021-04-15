from django.urls import path, include, re_path
from .views import AuthorizeUser, RegisterAPI, LoginAPI, UserAPI, DashBoardData, StrategyList, ExchangeList, ConnectExchange, GetConnectedExchanges, ConnectStrategy, GetConnectedStrategies, StrategyPairs, OrdersList, BugReport, TopUpStrategy, FacebookLogin, GoogleLogin 
from django.views.generic import TemplateView
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    path('api-token-auth/', obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
    path('api-token-verify/', verify_jwt_token),
    path('authorize-user/', AuthorizeUser.as_view()),
    path('rest-auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path('rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    
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