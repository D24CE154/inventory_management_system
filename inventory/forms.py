from django.forms import ModelForm
from .models import Product, ProductCategory, ProductItems, Brand
from django import forms
from django.db.models import Q

CATEGORY_SPEC_FIELDS = {
    'Smartphones': ['color', 'ram', 'storage', 'battery', 'processor'],
    'Audio': ['color', 'battery_life', 'connectivity', 'type'],
    'Wearables': ['color', 'screen_size', 'battery_life', 'features'],
    'Accessories': []
}

class CategoryForm(ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['category_name']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'})
        }
        labels = {
            'category_name': 'Category Name'
        }
        help_texts = {
            'category_name': 'Enter one of: Mobile, Tablet, Audio, Accessories'
        }

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].strip()
        duplicate_query = ProductCategory.objects.filter(category_name__iexact=category_name)
        similar_names_query = ProductCategory.objects.filter(
            Q(category_name__icontains=category_name) |
            Q(category_name__in=ProductCategory.objects.values_list('category_name', flat=True).filter(
                category_name__in=[word for word in category_name.split() if len(word) > 3]
            ))
        )
        if self.instance.pk:
            duplicate_query = duplicate_query.exclude(pk=self.instance.pk)
            similar_names_query = similar_names_query.exclude(pk=self.instance.pk)
        if duplicate_query.exists():
            raise forms.ValidationError(f"A category with name '{category_name}' already exists.")
        if similar_names_query.exists():
            similar_name = similar_names_query.first().category_name
            raise forms.ValidationError(
                f"This category is too similar to existing category '{similar_name}'. "
                f"Please use a more distinct name."
            )
        return category_name

class BrandForm(ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name', 'categories']
        widgets = {
            'brand_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Brand Name'}),
            'categories': forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'})
        }
        labels = {
            'brand_name': 'Brand Name',
            'categories': 'Categories'
        }

    def clean_brand_name(self):
        brand_name = self.cleaned_data['brand_name'].strip()
        if Brand.objects.filter(brand_name__iexact=brand_name).exists():
            raise forms.ValidationError(f"A brand with name '{brand_name}' already exists.")
        return brand_name

    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if not categories:
            raise forms.ValidationError("At least one category must be selected.")
        return categories

class ProductForm(ModelForm):
    category_id = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-select'}),
        label="Category",
        empty_label="Select Category"
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'brand-select'}),
        label="Brand",
        empty_label="Select Brand",
        required=False
    )

    class Meta:
        model = Product
        fields = ['product_name', 'category_id', 'brand', 'stock']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # Start with all brands to ensure the dropdown isn't empty
        self.fields['brand'].queryset = Brand.objects.all()
        if 'category_id' in self.data:
            try:
                category_id = int(self.data.get('category_id'))
                self.fields['brand'].queryset = Brand.objects.filter(categories__category_id=category_id).distinct()
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.pk and self.instance.category_id:
            # For existing products, filter brands by their category
            self.fields['brand'].queryset = Brand.objects.filter(
                categories__category_id=self.instance.category_id.category_id
            ).distinct()

class ProductItemsForm(ModelForm):
    class Meta:
        model = ProductItems
        fields = ['serial_number', 'price', 'image']
        widgets = {
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Serial Number'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)
        if category:
            spec_fields = CATEGORY_SPEC_FIELDS.get(category.category_name, [])
            for field in spec_fields:
                self.fields[field] = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': field.capitalize()}))

    def clean(self):
        cleaned_data = super().clean()
        specifications = {}
        for field in self.fields:
            if field not in ['serial_number', 'price', 'image']:
                specifications[field] = cleaned_data.pop(field, None)
        cleaned_data['specifications'] = specifications
        return cleaned_data