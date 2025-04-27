from django.forms import ModelForm
from .models import Product, ProductItem, ProductCategory, Brand
from django import forms


CATEGORY_SPEC_FIELDS = {
    'Mobile': ['RAM', 'Space', 'Processor'],
    'Audio': ['Wired/Wireless', 'Driver Size'],
    'Accessories': ['Color', 'Compatibility']
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

class ProductItemForm(forms.ModelForm):
    class Meta:
        model = ProductItem
        fields = ['serial_number', 'quantity', 'cost_price', 'sale_price']

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category', None)  # Get the category from kwargs
        super().__init__(*args, **kwargs)

        # Dynamically add category-specific fields
        if self.category in CATEGORY_SPEC_FIELDS:
            for field in CATEGORY_SPEC_FIELDS[self.category]:
                self.fields[field] = forms.CharField(
                    required=True,
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': field})
                )

        # Handle item_type and quantity fields based on category
        if self.category == "Accessories":
            self.fields['item_type'] = forms.CharField(
                initial=ProductItem.NON_SERIAL,
                widget=forms.HiddenInput()
            )
            self.fields['serial_number'].widget = forms.HiddenInput()  # Hide IMEI field
        else:
            self.fields['item_type'] = forms.CharField(
                initial=ProductItem.SERIALIZED,
                widget=forms.HiddenInput()
            )
            self.fields['quantity'].widget = forms.HiddenInput()
            self.fields['quantity'].initial = 1

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