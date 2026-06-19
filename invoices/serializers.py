from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.orderid', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'invoiceid',
            'order',
            'order_id',
            'invoice_number',
            'invoice_file',
            'created_at',
        ]