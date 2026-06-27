from django.db import models
from django.conf import settings
from orders.models import Order, OrderItem


class ReturnRequest(models.Model):
    RETURN_STATUS = (
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    )

    returnid = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="return_requests"
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="returns"
    )

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="returns"
    )

    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=RETURN_STATUS,
        default="requested"
    )

    admin_note = models.TextField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return #{self.returnid}"