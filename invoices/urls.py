from django.urls import path

from .views import (
    MyInvoicesView,
    InvoiceDetailView,
    GenerateInvoiceView,
)

urlpatterns = [
    path('', MyInvoicesView.as_view()),
    path('/<int:pk>', InvoiceDetailView.as_view()),
    path('/generate/<int:order_id>', GenerateInvoiceView.as_view()),
]