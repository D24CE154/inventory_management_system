from django.db import models

# Create your models here.
class Employee(models.Model):
    roleType = [
        ('Admin', 'Admin'),
        ('Sales Executive', 'Sales Executive'),
        ('Inventory Manager', 'Inventory Manager')
    ]

    employee_id = models.AutoField(primary_key=True)
    employee_username = models.CharField(max_length=255, null=False, blank=False)
    employee_password = models.CharField(max_length=255)
    role = models.CharField(choices=roleType, max_length=20, null=False, default='Sales Executive')  # Added max_length
    phone = models.CharField(max_length=15, null=False, blank=False)
    email = models.CharField(max_length=255, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    photo = models.ImageField(null=False, blank=False)