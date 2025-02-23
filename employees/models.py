from django.db import models
from django.utils import timezone

ROLE_CHOICES = [
    ('Admin', 'Admin'),
    ('Inventory Manager', 'Inventory Manager'),
    ('Sales Executive', 'Sales Executive'),
]

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Sales Executive')
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_valid = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.full_name} ({self.role})"

class AuditLog(models.Model):
    auditlog_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)