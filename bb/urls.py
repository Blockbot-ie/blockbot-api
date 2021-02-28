from django.urls import path
from .views import current_user, UserList, StrategyList, ExchangeList

urlpatterns = [
    path('current_user/', current_user),
    path('users/', UserList.as_view()),
    path('strategies/', StrategyList.as_view()),
    path('exchanges/', ExchangeList.as_view())
]