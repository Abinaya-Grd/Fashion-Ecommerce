from django.urls import path

from .views import (
    CreatePaymentView,
    MyPaymentsView,
    CreateRazorpayOrderView,
    VerifyRazorpayPaymentView,
)

urlpatterns = [

    path('', MyPaymentsView.as_view()),

    path('/create', CreatePaymentView.as_view()),

    path(
        '/create-razorpay-order',
        CreateRazorpayOrderView.as_view()
    ),

    path(
        '/verify-razorpay-payment',
        VerifyRazorpayPaymentView.as_view()
    ),
]