from django.urls import path, include
from .views import RegisterAPI, LoginAPI, UserAPI, StrategyList, ExchangeList
from knox import views as knox_views

urlpatterns = [
    path('auth', include('knox.urls')),
    path('auth/register', RegisterAPI.as_view()),
    path('auth/login', LoginAPI.as_view()),
    path('auth/user', UserAPI.as_view()),
    path('auth/logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('strategies/', StrategyList.as_view()),
    path('exchanges/', ExchangeList.as_view())
]