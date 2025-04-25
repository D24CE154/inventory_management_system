from django import forms
from django.forms import modelformset_factory

from inventory.models import ProductItem
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
    class Meta:
        model = SaleItem
        fields = ['product_id', 'quantity']
        widgets = {
            'product_id': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

SaleItemFormSet = modelformset_factory(
    SaleItem,
    form=SaleItemForm,
    extra=1,
    can_delete=True,
)
