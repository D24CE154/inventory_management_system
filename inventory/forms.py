from django.forms import ModelForm
from .models import Product, ProductCategory, ProductItems, NonSerializedProducts
from django import forms
from django.db.models import Q

class CategoryForm(ModelForm):

    class Meta:
        model = ProductCategory
        fields = ['category_name']

        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'})
        }
        labels = {
            'category_name' : 'Category Name'
        }
        help_texts = {
            'category_name' : 'Enter one of : Mobile, Tablet, Audio, Accessories'
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