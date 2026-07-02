from django.urls import path

from .views import (
    PurchaseReturnListCreateView,
    PurchaseReturnDetailView,
    ApprovePurchaseReturnView,
    RejectPurchaseReturnView,
    CompletePurchaseReturnView,
)

urlpatterns = [
    path('', PurchaseReturnListCreateView.as_view()),
    path('/<int:pk>', PurchaseReturnDetailView.as_view()),
    path('/<int:pk>/approve', ApprovePurchaseReturnView.as_view()),
    path('/<int:pk>/reject', RejectPurchaseReturnView.as_view()),
    path('/<int:pk>/complete', CompletePurchaseReturnView.as_view()),
]