from django.urls import path, include
from .views import UserAPI, UserList, StrategyList, ExchangeList
from knox import views as knox_views

urlpatterns = [
    path('auth', include('knox.urls')),
    path('auth/logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('auth/user', UserAPI.as_view()),
    path('users/', UserList.as_view()),
    path('strategies/', StrategyList.as_view()),
    path('exchanges/', ExchangeList.as_view())
]