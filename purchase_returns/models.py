from django.db import models
from purchases.models import Purchase, PurchaseItem
from suppliers.models import Supplier


class PurchaseReturn(models.Model):

    STATUS_CHOICES = (
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    )

    purchasereturnid = models.AutoField(primary_key=True)

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="purchase_returns"
    )

    purchase_item = models.ForeignKey(
        PurchaseItem,
        on_delete=models.CASCADE,
        related_name="purchase_returns"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="purchase_returns"
    )

    quantity = models.PositiveIntegerField()

    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    reason = models.TextField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="requested"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase Return #{self.purchasereturnid}"