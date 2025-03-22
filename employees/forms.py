from django import forms
from django.contrib.auth.models import User
from .models import Employee
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from PIL import Image

class SignupForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Enter a valid email address.")
    phone = forms.CharField(max_length=10, required=True, help_text="Phone number must be 10 digits.")
    full_name = forms.CharField(max_length=255, required=True, help_text="Enter your full name.")
    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=8,
        help_text="Password must contain at least one uppercase, one lowercase, one number, and one special character."
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput(), help_text="Re-enter your password.")
    address = forms.CharField(widget=forms.Textarea, required=True, help_text="Enter your full address.")
    photo = forms.ImageField(required=True, help_text="Upload a profile picture (Max 2MB).")

    ROLE_CHOICES = (
        ('Sales Executive', 'Sales Executive'),
        ('Inventory Manager', 'Inventory Manager'),
        ('Admin', 'Admin'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, initial='Sales Executive')

    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'phone', 'password', 'confirm_password', 'address', 'photo', 'role']

    def clean_password(self):
        password = self.cleaned_data.get("password")
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

        if not re.match(pattern, password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long and include:\n"
                "- One uppercase letter\n"
                "- One lowercase letter\n"
                "- One number\n"
                "- One special character (@$!%*?&)"
            )

        return password  # ✅ Return raw password (Do NOT hash it here)

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get("confirm_password")
        password = self.cleaned_data.get("password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit() or len(phone) != 10:
            raise ValidationError("Phone number must be exactly 10 digits.")
        if Employee.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")

        try:
            img = Image.open(photo)
            img.verify()
        except Exception:
            raise forms.ValidationError("Invalid image file. Please upload a valid image.")

        max_size = 2 * 1024 * 1024  # 2MB limit
        if photo.size > max_size:
            raise forms.ValidationError("Image file too large (max 2MB)")

        return photo

    def save(self, commit=True):
        """Save the user with hashed password."""
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}),
        required=True
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))

class ForgotPassword(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}),
        required = True
    )

class ResetPasswordForm(SignupForm):

    class Meta:
        model = Employee
        fields = ["password", "confirm_password"]

    def __init__(self, *args, **kwargs):
        """Remove unnecessary fields from SignupForm."""
        super().__init__(*args, **kwargs)
        for field in ["email", "phone", "full_name", "address", "photo"]:
            self.fields.pop(field, None)

class EmployeeEditForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'New Password'})
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'})
    )

    # Change is_active from checkbox to dropdown
    STATUS_CHOICES = (
        (True, 'Active'),
        (False, 'Inactive')
    )
    is_active = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = Employee
        fields = ['full_name', 'phone', 'role', 'address', 'photo', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'role': forms.Select(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Address'}),
            'photo': forms.FileInput(attrs={'class': 'form-input'})
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')

        # Convert is_active from string to boolean
        is_active = cleaned_data.get('is_active')
        if is_active == 'True':
            cleaned_data['is_active'] = True
        elif is_active == 'False':
            cleaned_data['is_active'] = False

        return cleaned_data