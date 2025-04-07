from django import forms
from .models import Sale, SaleItem, Customer, Product

class SaleForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=255)
    address = forms.CharField(max_length=255)
    payment_method = forms.ChoiceField(choices=Sale.paymentMethods)

    class Meta:
        model = Sale
        fields = ['customer_name', 'phone', 'address', 'payment_method']

class SaleItemForm(forms.ModelForm):
    product_id = forms.ModelChoiceField(queryset=Product.objects.all(), label='Product')
    product_category = forms.ChoiceField(choices=[('Accessories', 'Accessories'), ('Electronics', 'Electronics')])
    imei = forms.CharField(max_length=255, required=False)
    check_availability = forms.BooleanField(required=False, label='Check Availability')

    class Meta:
        model = SaleItem
        fields = ['product_id', 'quantity', 'product_category', 'imei', 'check_availability']