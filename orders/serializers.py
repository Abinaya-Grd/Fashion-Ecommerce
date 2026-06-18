from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_sku = serializers.CharField(source='variant.sku', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'orderitemid',
            'product',
            'product_name',
            'variant',
            'variant_sku',
            'quantity',
            'price',
            'total_price',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'orderid',
            'user',
            'items',
            'total_amount',
            'order_status',
            'payment_status',
            'shipping_address',
            'phone',
            'created_at',
            'updated_at',
        ]

        extra_kwargs = {
            'user': {'read_only': True}
        }