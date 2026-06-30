from django.db import models


class Supplier(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    supplierid = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=150, blank=True, null=True)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    gst_number = models.CharField(max_length=30, blank=True, null=True)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=10)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name