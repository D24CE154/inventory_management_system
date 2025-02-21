from django.db import models
from django.utils import timezone

from employees.models import Employee
from inventory.models import Products, ProductItems


class Customers(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255,null=False,blank=False)
    customer_address = models.CharField(max_length=255,null=False,blank=False)
    customer_phone = models.CharField(max_length=255,null=False,blank=False)
# Create your models here.
class Sales(models.Model):
    paymentMethods = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI')
    ]
    sale_id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(Employee, null=False, on_delete=models.CASCADE)
    customer_id = models.ForeignKey('Customers', null=False, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    payment_method = models.CharField(choices=paymentMethods, max_length=10, null=False, blank=False)
    sale_data = models.DateTimeField(auto_now_add=True)

class SaleItems(models.Model):
    saleitem_id = models.AutoField(primary_key=True)
    sale_id = models.ForeignKey(Sales,null=False,on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products,null=False,on_delete=models.CASCADE)
    imei = models.ForeignKey(ProductItems,null=True,on_delete=models.SET_NULL)
    quantity = models.IntegerField(null=False,blank=False)
    selling_price = models.DecimalField(max_digits=10,decimal_places=2,null=False,blank=False)
