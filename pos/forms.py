from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["customer_name", "customer_address", "customer_phone","customer_email"]

class SaleForm(forms.Form):
    customer = forms.IntegerField()
    payment_method = forms.ChoiceField(choices=[("Cash", "Cash"), ("UPI", "UPI")])