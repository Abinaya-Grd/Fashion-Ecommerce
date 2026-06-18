from rest_framework import serializers
from .models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    product_image = serializers.ImageField(
        source='product.thumbnail',
        read_only=True
    )

    variant_sku = serializers.CharField(
        source='variant.sku',
        read_only=True
    )

    class Meta:
        model = Wishlist
        fields = [
            'wishlistid',
            'user',
            'product',
            'product_name',
            'product_price',
            'product_image',
            'variant',
            'variant_sku',
            'created_at',
        ]

        extra_kwargs = {
            'user': {'read_only': True}
        }