from django.urls import path, include, re_path
from .views import RegisterAPI, LoginAPI, UserAPI, DashBoardData, StrategyList, ExchangeList, ConnectExchange, GetConnectedExchanges, ConnectStrategy, GetConnectedStrategies, StrategyPairs, OrdersList, BugReport, TopUpStrategy, FacebookLogin, GoogleLogin 
from django.views.generic import TemplateView
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView, ConfirmEmailView
from dj_rest_auth.views import LoginView, LogoutView

urlpatterns = [
    path('accounts/', include('allauth.urls'), name='socialaccount_signup'),
    path('account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('verify-email/',
         VerifyEmailView.as_view(), name='rest_verify_email'),
    path('account-confirm-email/',
         VerifyEmailView.as_view(), name='account_email_verification_sent'),
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$',
            VerifyEmailView.as_view(), name='account_confirm_email'),
    
    path('dj-rest-auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('password-reset/', PasswordResetView.as_view()),
    path('password-reset-confirm/<slug:uidb64>/<slug:token>/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

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