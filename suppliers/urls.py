from django.urls import path

from .views import (
    SupplierListCreateView,
    SupplierDetailView,
    ActiveSupplierView,
)

urlpatterns = [

    path("", SupplierListCreateView.as_view()),

    path("/active", ActiveSupplierView.as_view()),

    path("/<int:pk>", SupplierDetailView.as_view()),

]