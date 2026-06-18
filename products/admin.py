from django.contrib import admin
from .models import Product, ProductImage, Color, Size, ProductVariant

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(ProductVariant)