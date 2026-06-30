from rest_framework import serializers
from .models import Inventory, StockTransaction


class StockTransactionSerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(
        source="inventory.variant.sku",
        read_only=True
    )

    class Meta:
        model = StockTransaction
        fields = "__all__"


class InventorySerializer(serializers.ModelSerializer):
    sku = serializers.CharField(
        source="variant.sku",
        read_only=True
    )

    product_name = serializers.CharField(
        source="variant.product.name",
        read_only=True
    )

    class Meta:
        model = Inventory
        fields = "__all__"