from django.urls import path

from .views import (
    CreateOrderFromCartView,
    MyOrdersView,
    OrderDetailView,
)

urlpatterns = [

    path('', MyOrdersView.as_view()),

    path('/create', CreateOrderFromCartView.as_view()),

    path('/<int:pk>', OrderDetailView.as_view()),
]