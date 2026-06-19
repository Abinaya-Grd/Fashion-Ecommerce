from django.db import models
from orders.models import Order


class Payment(models.Model):

    PAYMENT_METHODS = (
        ('cod', 'Cash On Delivery'),
        ('razorpay', 'Razorpay'),
    )

    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    paymentid = models.AutoField(primary_key=True)

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Payment #{self.paymentid}"