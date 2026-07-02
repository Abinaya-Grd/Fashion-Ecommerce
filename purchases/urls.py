from django.urls import path

from .views import (
    PurchaseListCreateView,
    PurchaseDetailView,
    ReceivePurchaseView,
    UpdatePurchaseStatusView,
)

urlpatterns = [
    path('', PurchaseListCreateView.as_view()),
    path('/<int:pk>', PurchaseDetailView.as_view()),
    path('/<int:pk>/receive', ReceivePurchaseView.as_view()),
    path('/<int:pk>/status', UpdatePurchaseStatusView.as_view()),
]