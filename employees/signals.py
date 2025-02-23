from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Employee

@receiver(user_signed_up)
def google_signup_handler(request, user, **kwargs):
    """Create an Employee entry for Google signups if not already created."""
    if not Employee.objects.filter(email=user.email).exists():
        Employee.objects.create(
            full_name=user.first_name + " " + user.last_name if user.first_name or user.last_name else user.email,
            email=user.email,
            password="",
            role="Sales Executive",
            phone="0000000000",
            address="Default Address",
            otp_valid=True
        )