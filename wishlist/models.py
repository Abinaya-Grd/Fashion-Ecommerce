from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant


class Wishlist(models.Model):
    wishlistid = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product', 'variant')

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"