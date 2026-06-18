from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_total = serializers.DecimalField( source='order.total_amount',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

       
    class Meta:
        model = Payment
        fields = '__all__'