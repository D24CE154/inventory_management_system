#point of sales model


from django.db import models
from django.utils import timezone

from employees.models import Employee
from inventory.models import Product, ProductItem


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255,null=False,blank=False)
    customer_address = models.CharField(max_length=255,null=False,blank=False)
    customer_phone = models.CharField(max_length=255,null=False,blank=False,unique=True)

class Sale(models.Model):
    paymentMethods = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI')
    ]
    sale_id = models.AutoField(primary_key=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    employee_id = models.ForeignKey(Employee, null=False, on_delete=models.CASCADE)
    customer_id = models.ForeignKey('pos.Customer', null=False, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    payment_method = models.CharField(choices=paymentMethods, max_length=10, null=False, blank=False)
    sale_date = models.DateTimeField(auto_now_add=True)
    invoice_file = models.FileField(upload_to='invoices/', null=True, blank=True)

class SaleItem(models.Model):
    saleitem_id = models.AutoField(primary_key=True)
    sale_id = models.ForeignKey(Sale, null=False, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, null=False, on_delete=models.CASCADE)
    imei = models.ForeignKey(ProductItem,null=True,on_delete=models.SET_NULL)
    quantity = models.IntegerField(null=False,blank=False)
    selling_price = models.DecimalField(max_digits=10,decimal_places=2,null=False,blank=False)
