from rest_framework import serializers
from .models import ReturnRequest


class ReturnRequestSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="order_item.product.name",
        read_only=True
    )

    class Meta:
        model = ReturnRequest
        fields = [
            "returnid",
            "user",
            "order",
            "order_item",
            "product_name",
            "reason",
            "status",
            "admin_note",
            "refund_amount",
            "requested_at",
            "updated_at",
        ]

        read_only_fields = [
            "user",
            "status",
            "admin_note",
            "refund_amount",
            "requested_at",
            "updated_at",
        ]