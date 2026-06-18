from django.contrib import admin
from .models import CustomUser, Address, OTP

admin.site.register(CustomUser)
admin.site.register(Address)
admin.site.register(OTP)