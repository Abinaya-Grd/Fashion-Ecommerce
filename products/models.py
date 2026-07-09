from django.db import models
from django.conf import settings
from django.utils.text import slugify
from categories.models import Category, SubCategory, ProductStyle, Brand


class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    productid = models.AutoField(primary_key=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    product_style = models.ForeignKey(
        ProductStyle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, unique=True)

    # Product SKU optional. Variant SKU is the main stock SKU.
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='products/', blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    is_in_stock = models.BooleanField(default=True)

    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_unique_slug(self):
        base_slug = slugify(self.name)
        slug = base_slug
        count = 1

        while Product.objects.filter(slug=slug).exclude(productid=self.productid).exists():
            slug = f"{base_slug}-{count}"
            count += 1

        return slug

    def generate_product_sku(self):
        base_sku = slugify(self.name).upper().replace("-", "")
        sku = f"PROD-{base_sku}"
        count = 1

        while Product.objects.filter(sku=sku).exclude(productid=self.productid).exists():
            sku = f"PROD-{base_sku}-{count}"
            count += 1

        return sku

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()

        if not self.sku:
            self.sku = self.generate_product_sku()

        self.is_in_stock = self.stock > 0

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    imageid = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_images'
    )

    image = models.ImageField(upload_to='products/gallery/')
    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name


class Color(models.Model):
    colorid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    color_code = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return self.name


class Size(models.Model):
    sizeid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    variantid = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Auto generated. No need to type manually.
    sku = models.CharField(max_length=150, unique=True, blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    is_in_stock = models.BooleanField(default=True)

    status = models.CharField(max_length=20, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'color', 'size')

    def generate_variant_sku(self):
        product_part = slugify(self.product.name).upper().replace("-", "")

        color_part = "NA"
        if self.color:
            color_part = slugify(self.color.name).upper().replace("-", "")

        size_part = "NA"
        if self.size:
            size_part = slugify(self.size.name).upper().replace("-", "")

        base_sku = f"{product_part}-{color_part}-{size_part}"
        sku = base_sku
        count = 1

        while ProductVariant.objects.filter(sku=sku).exclude(variantid=self.variantid).exists():
            sku = f"{base_sku}-{count}"
            count += 1

        return sku

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_variant_sku()

        self.is_in_stock = self.stock > 0

        super().save(*args, **kwargs)

    def __str__(self):
        return self.sku
    
    from django.conf import settings


class RecentlyViewedProduct(models.Model):
    viewedid = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recently_viewed"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="viewed_by"
    )

    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.email} viewed {self.product.name}"