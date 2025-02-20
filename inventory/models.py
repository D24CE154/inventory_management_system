from django.db import models

# Create your models here.
class ProductCategories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255,null=False,unique=True)

class Manufacturers(models.Model):
    manufacturer_id = models.AutoField(primary_key=True)
    manufacturer_name = models.CharField(max_length=255,null=False,unique=True)
    contact_info = models.CharField(max_length=255,null=False,unique=True)

class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,null=False)
    category_id = models.ForeignKey(ProductCategories,null=False,on_delete=models.CASCADE)
    manufacturer_id = models.ForeignKey(Manufacturers,null=False,on_delete=models.CASCADE)
    stock = models.IntegerField(null=False,default=0)
    serialized_stock = models.IntegerField(null=False,default=0)
    image = models.CharField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SerializedProducts(models.Model):
    productStatus = [('Available','Available'),('Sold','Sold')]

    instance_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Products,null=False,on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=255,null=False,unique=True)
    specifications = models.JSONField(default=dict)
    status = models.CharField(choices=productStatus,null=False,default='Available')
    created_at = models.DateTimeField(auto_now_add=True)

class NonSerializedProducts (models.Model):
    product_id = models.ForeignKey(Products,null=False,on_delete=models.CASCADE)
    purchase_price = models.IntegerField(null=False,default=0)
