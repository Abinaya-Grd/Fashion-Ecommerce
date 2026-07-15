from django.db import models


class Banner(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    DEVICE_CHOICES = (
        ("web", "Web"),
        ("mobile", "Mobile"),
        ("both", "Both"),
    )
    
    BANNER_TYPE = (
    ("hero", "Hero"),
    ("festival", "Festival"),
     )

    banner_type = models.CharField(
    max_length=20,
    choices=BANNER_TYPE,
    default="hero"
     )
    bannerid = models.AutoField(primary_key=True)

    title = models.CharField(max_length=200)

    subtitle = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to="banners/"
    )

    button_text = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    button_link = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    device = models.CharField(
        max_length=20,
        choices=DEVICE_CHOICES,
        default="both"
    )

    display_order = models.PositiveIntegerField(default=1)

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.title