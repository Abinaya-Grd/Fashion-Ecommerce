from django.urls import path

from .views import (
    ReportsDashboardView,
    SalesReportView,
    OrdersReportView,
    ProductsReportView,
    CustomersReportView,
    RevenueReportView,
)

urlpatterns = [
    path('/dashboard', ReportsDashboardView.as_view()),
    path('/sales', SalesReportView.as_view()),
    path('/orders', OrdersReportView.as_view()),
    path('/products', ProductsReportView.as_view()),
    path('/customers', CustomersReportView.as_view()),
    path('/revenue', RevenueReportView.as_view()),
]