from django.db import models
from suppliers.models import Supplier
from products.models import ProductVariant


class Purchase(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("ordered", "Ordered"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    )

    purchaseid = models.AutoField(primary_key=True)

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="purchases"
    )

    invoice_number = models.CharField(max_length=100, unique=True)

    purchase_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number


class PurchaseItem(models.Model):

    purchaseitemid = models.AutoField(primary_key=True)

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.variant.sku