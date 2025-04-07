# Inventory models

from django.db import models

class ProductCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255,null=False,blank=False)

    def __str__(self):
        return self.category_name

class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    categories = models.ManyToManyField(ProductCategory, related_name="brands")

    def __str__(self):
        return f"{self.brand_name}"

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255, null=False, blank=False)
    category_id = models.ForeignKey(ProductCategory, null=False, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, null=True, on_delete=models.CASCADE)
    stock = models.IntegerField(null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        self.productitems_set.all().delete()
        super().delete(*args, **kwargs)

class ProductItems(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('Serialized', 'Serialized'),
        ('NonSerialized', 'NonSerialized'),
    ]

    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    product_type = models.CharField(max_length=15, choices=PRODUCT_TYPE_CHOICES, default='Serialized')
    serial_number = models.CharField(max_length=255, null=True, blank=True, unique=True)
    specifications = models.JSONField(default=dict)  # Category-specific specs
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='Available')
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
