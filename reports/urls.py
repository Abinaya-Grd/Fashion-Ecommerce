from django.urls import path

from .views import (
    ReportsDashboardView,
    SalesReportView,
    OrdersReportView,
    ProductsReportView,
    CustomersReportView,
    RevenueReportView,
    ExportOrdersCSVView,
    ExportProductsCSVView,
    ExportSalesCSVView,
)

urlpatterns = [
    path('/dashboard', ReportsDashboardView.as_view()),
    path('/sales', SalesReportView.as_view()),
    path('/orders', OrdersReportView.as_view()),
    path('/products', ProductsReportView.as_view()),
    path('/customers', CustomersReportView.as_view()),
    path('/revenue', RevenueReportView.as_view()),

    path('/export/orders-csv', ExportOrdersCSVView.as_view()),
    path('/export/products-csv', ExportProductsCSVView.as_view()),
    path('/export/sales-csv', ExportSalesCSVView.as_view()),
]