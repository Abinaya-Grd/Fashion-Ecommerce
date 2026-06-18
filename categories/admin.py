from django.contrib import admin
from .models import Category, SubCategory, ProductStyle, Brand

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(ProductStyle)
admin.site.register(Brand)