from django import forms
from supplier.models import Supplier
import re

class SupplierForm(forms.ModelForm):
    supplier_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Company name'}),
        help_text='Enter the name of Company.'
    )
    contact_person = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'contact person'}),
        help_text='Enter the name of the contact person.'
    )
    supplier_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel','placeholder':'Phone number'}),
        help_text='Enter a valid phone number (e.g., +91-XXXXXXXXXX).'
    )
    supplier_mail = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'Email'}),
        help_text='Enter a valid email address for communication.'
    )
    supplier_address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,'placeholder':'Address'}),
        help_text='Enter the complete postal address of the supplier.'
    )

    class Meta:
        model = Supplier
        fields = ['supplier_name', 'contact_person', 'supplier_phone',
                  'supplier_mail', 'supplier_address']

    def clean_supplier_name(self):
        name = self.cleaned_data.get('supplier_name')
        if len(name.strip()) < 2:
            raise forms.ValidationError("Supplier name must be at least 2 characters long.")
        return name.strip()

    def clean_contact_person(self):
        contact = self.cleaned_data.get('contact_person')
        if len(contact.strip()) < 2:
            raise forms.ValidationError("Contact person name must be at least 2 characters long.")
        if re.search(r'[0-9]', contact):
            raise forms.ValidationError("Contact person name should not contain numbers.")
        return contact.strip()

    def clean_supplier_phone(self):
        phone = self.cleaned_data.get('supplier_phone')
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', phone)
        if not (8 <= len(digits_only) <= 15):
            raise forms.ValidationError("Phone number must be between 8 and 15 digits.")
        if not re.match(r'^[0-9\s\-\+]+$', phone):
            raise forms.ValidationError("Please enter a valid phone number format.")
        return phone

    def clean_supplier_mail(self):
        email = self.cleaned_data.get('supplier_mail')
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise forms.ValidationError("Please enter a valid email address.")
        return email.lower()

    def clean_supplier_address(self):
        address = self.cleaned_data.get('supplier_address')
        if len(address.strip()) < 10:
            raise forms.ValidationError("Please provide a complete address (at least 10 characters).")
        return address.strip()