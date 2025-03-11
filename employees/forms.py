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

    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'phone', 'password', 'confirm_password', 'address', 'photo']

    def clean_password(self):
        """Ensure password meets security requirements but DO NOT hash it here."""
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
        """Ensure passwords match BEFORE hashing."""
        confirm_password = self.cleaned_data.get("confirm_password")
        password = self.cleaned_data.get("password")  # ✅ Now both are raw

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return confirm_password

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        """Ensure phone number is exactly 10 digits."""
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit() or len(phone) != 10:
            raise ValidationError("Phone number must be exactly 10 digits.")
        if Employee.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

    def clean_photo(self):
        """Validate and resize photo if needed."""
        photo = self.cleaned_data.get("photo")

        try:
            img = Image.open(photo)
            img.verify()  # Check if it's a valid image file
        except Exception:
            raise forms.ValidationError("Invalid image file. Please upload a valid image.")

        # Max size check (2MB)
        max_size = 2 * 1024 * 1024  # 2MB limit
        if photo.size > max_size:
            raise forms.ValidationError("Image file too large (max 2MB)")

        return photo

    def save(self, commit=True):
        """Save the user with hashed password."""
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])  # ✅ Hash password here
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}),
        required=True
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
