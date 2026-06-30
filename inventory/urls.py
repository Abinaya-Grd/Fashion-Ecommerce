from django.urls import path
from .views import (
    InventoryListView,
    InventoryDetailView,
    StockInView,
    StockOutView,
    StockAdjustmentView,
    LowStockView,
    OutOfStockView,
    StockHistoryView,
)

urlpatterns = [
    path('', InventoryListView.as_view()),

    path('/stock-in', StockInView.as_view()),
    path('/stock-out', StockOutView.as_view()),
    path('/adjustment', StockAdjustmentView.as_view()),
    path('/low-stock', LowStockView.as_view()),
    path('/out-of-stock', OutOfStockView.as_view()),
    path('/history/<int:variant_id>', StockHistoryView.as_view()),
    path('/<int:pk>', InventoryDetailView.as_view()),
]