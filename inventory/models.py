from django.db import models
from django.conf import settings
from products.models import ProductVariant


class Inventory(models.Model):
    inventoryid = models.AutoField(primary_key=True)

    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="inventory"
    )

    available_stock = models.PositiveIntegerField(default=0)

    reserved_stock = models.PositiveIntegerField(default=0)

    damaged_stock = models.PositiveIntegerField(default=0)

    reorder_level = models.PositiveIntegerField(default=10)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.variant.sku


class StockTransaction(models.Model):

    TRANSACTION_TYPES = (
        ("stock_in", "Stock In"),
        ("stock_out", "Stock Out"),
        ("adjustment", "Adjustment"),
    )

    transactionid = models.AutoField(primary_key=True)

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    quantity = models.PositiveIntegerField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.transaction_type} - {self.inventory.variant.sku}"