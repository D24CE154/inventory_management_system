# Inventory models

from django.db import models
from django.db.models import Sum


class ProductCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    categories = models.ManyToManyField(ProductCategory, related_name="brands")

    def __str__(self):
        return self.name

class Product(models.Model):
    name     = models.CharField(max_length=255)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def total_stock(self):
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0


class ProductItem(models.Model):
    SERIALIZED = "Serialized"
    NON_SERIAL = "NonSerialized"
    ITEM_TYPE  = [(SERIALIZED, "Serialized"), (NON_SERIAL, "Non‑Serialized")]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=15, choices=ITEM_TYPE)
    serial_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    specifications = models.JSONField(default=dict, blank=True)
