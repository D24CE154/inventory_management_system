from django.db import models

from inventory.models import NonSerializedProducts


# Create your models here.
class Suppliers (models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,null=False)
    contact_person = models.CharField(max_length=255,null=False)
    phone_number = models.CharField(max_length=255,null=False)
    email = models.CharField(max_length=255,null=False)
    address = models.CharField(max_length=255,null=False)
    created = models.DateTimeField(auto_now_add=True)

class PurchaseOrders(models.Model):
    shipmentStatus = [('Pending','Pending'), ('Accepted','Accepted'),
                      ('Shipped','Shipped') ,('Delivered','Delivered'),
                      ('Cancelled','Cancelled')]

    purchase_order_id = models.AutoField(primary_key=True)
    supplier_id = models.ForeignKey(Suppliers,null=False,on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10,decimal_places=2,null=False)
    status = models.CharField(choices=shipmentStatus,default='Pending',max_length=20)
    received_date = models.DateField(null=False)

class PurchaseOrderItems(models.Model):
    purchase_item_id = models.AutoField(primary_key=True)
    purchase_order_id = models.ForeignKey(PurchaseOrders,null=False,on_delete=models.CASCADE)
    product_id = models.ForeignKey(NonSerializedProducts,null=False,on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)
    unit_cost = models.DecimalField(max_digits=10,decimal_places=2,null=False)

