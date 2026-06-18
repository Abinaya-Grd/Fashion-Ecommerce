from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
)

urlpatterns = [
    path('', CartView.as_view()),
    path('/add', AddToCartView.as_view()),
    path('/update/<int:pk>', UpdateCartItemView.as_view()),
    path('/remove/<int:pk>', RemoveCartItemView.as_view()),
    path('/clear', ClearCartView.as_view()),
]