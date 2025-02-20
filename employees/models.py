from django.db import models

# Create your models here.
class Employee(models.Model):
    roleType = [('Admin','Admin'),
                ('Sales Executive','Sales Executive'),
                ('Inventory Manager','Inventory Manager')]

    employee_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255,null=False,unique=True)
    password = models.CharField(max_length=255)
    type = models.CharField(choices = roleType,null=False,default='Sales Executive')

