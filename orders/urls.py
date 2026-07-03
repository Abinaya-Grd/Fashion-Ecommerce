from django.urls import path

from .views import (
    CreateOrderFromCartView,
    MyOrdersView,
    OrderDetailView,
    CancelOrderView,
    UpdateOrderStatusView,
    OrderTrackingView,
    OrderSummaryView,
)

urlpatterns = [
    path('', MyOrdersView.as_view()),
    path('/create', CreateOrderFromCartView.as_view()),
    path('/<int:pk>', OrderDetailView.as_view()),
    path('/<int:pk>/cancel', CancelOrderView.as_view()),
    path('/<int:pk>/status', UpdateOrderStatusView.as_view()),
    path('/<int:pk>/tracking', OrderTrackingView.as_view()),
    path('/summary', OrderSummaryView.as_view()),
]