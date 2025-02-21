from django.db import models

# Create your models here.
class ProductCategories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255,null=False,blank=False)

class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255,null=False,blank=False)

    category_id = models.ForeignKey(ProductCategories,null=False,on_delete=models.CASCADE)

    stock = models.IntegerField(null=False,default=0)

    image = models.CharField(max_length=255,null=False,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductItems(models.Model):
    productStatus = [
        ('Available', 'Available'),
        ('Sold', 'Sold')
    ]

    product_id = models.ForeignKey('Products', null=False, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=255, null=False, unique=True)
    specifications = models.JSONField(default=dict)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)  # Added decimal_places
    status = models.CharField(choices=productStatus, max_length=10, null=False, default='Available')  # Added max_length
    created_at = models.DateTimeField(auto_now_add=True)

class NonSerializedProducts (models.Model):
    product_id = models.ForeignKey(Products,null=False,on_delete=models.CASCADE)
    nonserialized_price = models.IntegerField(null=False,default=0)
