from django.forms import ModelForm
from .models import Product, ProductItem, ProductCategory, Brand
from django import forms

CATEGORY_SPEC_FIELDS = {
    'Mobile': ['RAM', 'Storage', 'Processor', 'Display Size'],
    'Audio': ['Driver size', 'Wired/Wireless'],
    'Accessories': ['Color', 'Phone Compatibility']
}

class ProductForm(ModelForm):
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-select'}),
        label="Category",
        empty_label="Select Category"
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'brand-select'}),
        label="Brand",
        empty_label="Select Brand"
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'brand']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
        }

class ProductItemForm(ModelForm):
    category = forms.ChoiceField(
        choices=[(key, key) for key in CATEGORY_SPEC_FIELDS.keys()],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-select'})
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'brand-select', 'disabled': 'true'})
    )
    specifications = forms.JSONField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'specifications-field', 'disabled': 'true'}),
        required=False
    )

    class Meta:
        model = ProductItem
        fields = [
            'serial_number', 'item_type', 'quantity', 'cost_price', 'sale_price', 'image', 'specifications'
        ]
        widgets = {
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].widget.attrs.update({'disabled': 'true'})

class CategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
        }

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand Name'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }