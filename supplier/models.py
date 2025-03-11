#SUpplier model
from django.db import models
from inventory.models import NonSerializedProducts


# Create your models here.
class Supplier (models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255,null=False,blank=False)
    contact_person = models.CharField(max_length=255,null=False,blank=False)
    supplier_phone = models.CharField(max_length=20,null=False,blank=False)
    supplier_mail = models.CharField(max_length=255,null=False,blank=False)
    supplier_address = models.CharField(max_length=255,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

class PurchaseOrder(models.Model):
    shipmentStatus = [('Pending','Pending'), ('Accepted','Accepted'),
                      ('Shipped','Shipped') ,('Delivered','Delivered'),
                      ('Cancelled','Cancelled')]

    purchase_order_id = models.AutoField(primary_key=True)
    supplier_id = models.ForeignKey(Supplier, null=False, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10,decimal_places=2,null=False)
    status = models.CharField(choices=shipmentStatus,default='Pending',max_length=20)
    received_date = models.DateField(null=False)

class PurchaseOrderItem(models.Model):
    purchase_item_id = models.AutoField(primary_key=True)
    purchase_order_id = models.ForeignKey(PurchaseOrder, null=False, on_delete=models.CASCADE)
    product_id = models.ForeignKey(NonSerializedProducts,null=False,on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)
    unit_cost = models.DecimalField(max_digits=10,decimal_places=2,null=False)

