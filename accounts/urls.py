from django.urls import path

from .views import (
RegisterView,
LoginView,
VerifyEmailView,
ProfileView,
ChangePasswordView,
ForgotPasswordView,
ResetPasswordView,
AddressListCreateView,
AddressDetailView,
SetDefaultAddressView,
)

urlpatterns = [
path('register', RegisterView.as_view(), name='register'),
path('login', LoginView.as_view(), name='login'),

path('verify-email', VerifyEmailView.as_view(), name='verify-email'),

path('profile', ProfileView.as_view(), name='profile'),
path('change-password', ChangePasswordView.as_view(), name='change-password'),

path('forgot-password', ForgotPasswordView.as_view(), name='forgot-password'),
path('reset-password', ResetPasswordView.as_view(), name='reset-password'),

path('addresses', AddressListCreateView.as_view(), name='addresses'),
path('addresses/<int:pk>', AddressDetailView.as_view(), name='address-detail'),
path(
    'addresses/<int:pk>/set-default',
    SetDefaultAddressView.as_view(),
    name='set-default-address'
),

]
