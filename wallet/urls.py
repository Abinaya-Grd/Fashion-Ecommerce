from django.urls import path

from .views import (
    WalletView,
    WalletHistoryView,
    AddMoneyView,
    WithdrawMoneyView,
)

urlpatterns = [
    path('', WalletView.as_view()),
    path('/history', WalletHistoryView.as_view()),
    path('/add-money', AddMoneyView.as_view()),
    path('/withdraw', WithdrawMoneyView.as_view()),
]