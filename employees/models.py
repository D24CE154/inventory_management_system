from django.db import models
from django.utils import timezone

ROLE_CHOICES = [
    ('Sales Executive', 'Sales Executive'),
    ('Inventory Manager', 'Inventory Manager'),
    ('Owner', 'Owner'),
    ('Admin', 'Admin'),
]

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Sales Executive')
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True,default='defaultmail@gmail.com')
    address = models.TextField()
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='profile_pics/default_profile.jpg')
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_valid = models.BooleanField(default=False)

    password = models.CharField(max_length=128)  # Store hashed password
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.full_name


class AuditLog(models.Model):
    auditlog_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)