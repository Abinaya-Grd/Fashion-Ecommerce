from django.urls import path

from .views import (
    CouponListCreateView,
    CouponDetailView,
    ApplyCouponView,
)

urlpatterns = [
    path('', CouponListCreateView.as_view()),
    path('/<int:pk>', CouponDetailView.as_view()),
    path('/apply', ApplyCouponView.as_view()),
]