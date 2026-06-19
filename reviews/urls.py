from django.urls import path

from .views import (
    ReviewListCreateView,
    AddReviewView,
    ReviewDetailView,
    ProductRatingSummaryView,
)

urlpatterns = [
    path('', ReviewListCreateView.as_view()),
    path('/add', AddReviewView.as_view()),
    path('/<int:pk>', ReviewDetailView.as_view()),
    path('/summary/<int:product_id>', ProductRatingSummaryView.as_view()),
]