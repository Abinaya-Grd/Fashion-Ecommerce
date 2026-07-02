from rest_framework import serializers
from .models import Purchase, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(
        source="variant.sku",
        read_only=True
    )

    product_name = serializers.CharField(
        source="variant.product.name",
        read_only=True
    )

    class Meta:
        model = PurchaseItem
        fields = [
            "purchaseitemid",
            "variant",
            "variant_sku",
            "product_name",
            "quantity",
            "cost_price",
            "total_price",
        ]


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)

    supplier_name = serializers.CharField(
        source="supplier.company_name",
        read_only=True
    )

    class Meta:
        model = Purchase
        fields = [
            "purchaseid",
            "supplier",
            "supplier_name",
            "invoice_number",
            "purchase_date",
            "total_amount",
            "status",
            "remarks",
            "items",
            "created_at",
            "updated_at",
        ]