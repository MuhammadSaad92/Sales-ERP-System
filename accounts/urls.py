from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('balances/', OpeningBalanceListView.as_view(), name='opening_balance_list'),  # Changed to /balances/
    path('opening_balance_add/', OpeningBalanceCreateView.as_view(), name='opening_balance_add'),
]