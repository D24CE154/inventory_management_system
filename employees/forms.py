from django import forms
from .models import Employee
import re
from django.core.exceptions import ValidationError
from PIL import Image
from django.contrib.auth.hashers import make_password

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        min_length=8,
        max_length=15,
        help_text="Password must contain at least one uppercase, one lowercase, one number, and one special character."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        label="Confirm Password"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}),
        required=True
    )
    photo = forms.ImageField(required=True)

    class Meta:
        model = Employee
        fields = ['full_name', 'phone', 'email', 'address', 'password', 'confirm_password', 'photo']

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if len(password) > 15:
            raise forms.ValidationError("Password must be at most 15 characters long.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one number.")
        if not re.search(r'[@$!%*?&]', password):
            raise forms.ValidationError("Password must contain at least one special character (@$!%*?&).")

        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get("confirm_password")
        password = self.cleaned_data.get("password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Employee.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit() or len(phone) < 10:
            raise ValidationError("Invalid phone number. Please enter a valid number.")
        if Employee.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        try:
            img = Image.open(photo)
            img.verify()
        except:
            raise forms.ValidationError("Invalid image file.")

        max_size = 2 * 1024 * 1024
        if photo.size > max_size:
            raise forms.ValidationError("Image file too large (max 2MB)")

        return photo

    def save(self, commit=True):
        employee = super().save(commit=False)
        employee.password = make_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            employee.save()
        return employee


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}),
        required=True
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))