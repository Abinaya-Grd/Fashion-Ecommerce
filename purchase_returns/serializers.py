from rest_framework import serializers

from .models import PurchaseReturn


class PurchaseReturnSerializer(serializers.ModelSerializer):

    supplier_name = serializers.CharField(
        source="supplier.company_name",
        read_only=True
    )

    invoice_number = serializers.CharField(
        source="purchase.invoice_number",
        read_only=True
    )

    product_name = serializers.CharField(
        source="purchase_item.variant.product.name",
        read_only=True
    )

    variant_sku = serializers.CharField(
        source="purchase_item.variant.sku",
        read_only=True
    )

    class Meta:
        model = PurchaseReturn
        fields = [
            "purchasereturnid",
            "purchase",
            "invoice_number",
            "purchase_item",
            "supplier",
            "supplier_name",
            "product_name",
            "variant_sku",
            "quantity",
            "refund_amount",
            "reason",
            "remarks",
            "status",
            "created_at",
            "updated_at",
        ]