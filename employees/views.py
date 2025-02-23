import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from .forms import SignupForm, LoginForm
from .models import Employee

# Helper to generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Email Signup View (two-step: initial signup and OTP verification)
def signup_view(request):
    if request.method == "POST":
        if 'otp' in request.POST:
            # OTP Verification
            entered_otp = request.POST.get("otp")
            email = request.session.get("signup_email")

            try:
                user = Employee.objects.get(email=email)
            except Employee.DoesNotExist:
                messages.error(request, "Session expired. Please sign up again.")
                return redirect("signup")

            if user.otp == entered_otp:
                user.otp_valid = True
                user.save()
                messages.success(request, "Signup successful! Please log in.")
                return redirect("login")
            else:
                messages.error(request, "Invalid OTP. Try again.")
                return render(request, "signup.html", {"otp_sent": True})

        else:
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.role = "Sales Executive"  # Default role
                user.otp = generate_otp()
                user.otp_valid = False
                user.save()

                # Store email in session for OTP verification
                request.session["signup_email"] = user.email

                # Send OTP via Email
                send_mail(
                    "Your OTP for Signup",
                    f"Your OTP is: {user.otp}",
                    "noreply@yourdomain.com",
                    [user.email],
                    fail_silently=False,
                )

                messages.info(request, "An OTP has been sent to your email.")
                return render(request, "signup.html", {"otp_sent": True})
            else:
                messages.error(request, "Passwords do not match")

    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})
# Email Login View
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                user = Employee.objects.get(email=email)
                if not user.otp_valid:
                    messages.error(request, "Your email is not verified. Please complete signup.")
                    return redirect("signup")
                # Check password using Django's check_password
                if check_password(password, user.password):
                    request.session["employee_id"] = user.employee_id
                    request.session["user_role"] = user.role
                    messages.success(request, "Login successful!")
                    if user.role == "Admin":
                        return redirect("../inventory/templates/admin_dashboard.html")
                    elif user.role == "Inventory Manager":
                        return redirect("/inventory/managerdashboard/")
                    else:
                        return redirect("inventory/templates/admin_dashboard.html")
                else:
                    messages.error(request, "Invalid email or password.")
            except Employee.DoesNotExist:
                messages.error(request, "User does not exist.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

# Logout View
def logout_view(request):
    request.session.flush()
    return redirect("login")


def redirect_based_on_role(request):
    if not request.user.is_authenticated:
        return redirect("login")
    email = request.session.get("signup_email")
    try:
        user = Employee.objects.get(email=email)
    except Employee.DoesNotExist:
        return redirect("login")

    if user.role == "Admin":
        return redirect("/inventory/admin_dashboard/")
    elif user.role == "Inventory Manager":
        return redirect("/inventory/manager_dashboard/")
    else:
        return redirect("/pos/sales_dashboard/")