import time
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings
from .models import Employee
from .forms import SignupForm, LoginForm

OTP_EXPIRY_SECONDS = 300
OTP_RESEND_LIMIT = 3

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    """Sends OTP to the given email address."""
    subject = 'Your OTP for Account Verification'
    message = f'Your OTP for account verification is: {otp}. Valid for 5 minutes.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def signup_view(request):
    if request.method == "POST":
        if "otp" in request.POST:
            entered_otp = request.POST.get("otp")
            if not request.session.get("signup_data"):
                messages.error(request, "Session expired. Please sign up again.")
                return redirect("signup")

            if time.time() - request.session.get("otp_timestamp", 0) > OTP_EXPIRY_SECONDS:
                messages.error(request, "OTP has expired. Request a new one.")
                return render(request, "signup.html", {"otp_sent": True, "otp_expired": True})

            if request.session["otp"] == entered_otp:
                signup_data = request.session.get("signup_data")

                employee = Employee(
                    full_name=signup_data["full_name"],
                    email=signup_data["email"],
                    phone=signup_data["phone"],
                    address=signup_data["address"],
                    password=make_password(signup_data["password"])
                )

                if 'photo_path' in request.session:
                    employee.photo = request.session['photo_path']

                employee.save()
                request.session.flush()
                messages.success(request, "Signup successful! Please log in.")
                return redirect("login")

            messages.error(request, "Invalid OTP. Try again.")
            return render(request, "signup.html", {"otp_sent": True})

        else:  # If signup form is submitted
            form = SignupForm(request.POST, request.FILES)
            if form.is_valid():
                # Don't save the form yet, just get the data
                employee = form.save(commit=False)

                email = form.cleaned_data["email"]
                otp = generate_otp()

                # Save form data to session
                request.session["signup_data"] = {
                    "full_name": form.cleaned_data["full_name"],
                    "email": form.cleaned_data["email"],
                    "phone": form.cleaned_data["phone"],
                    "address": form.cleaned_data["address"],
                    "password": form.cleaned_data["password"],
                }

                if 'photo' in request.FILES:
                    photo = request.FILES['photo']
                    # Store the file path in profile_pics folder in session
                    file_name = default_storage.save(f'profile_pics/{photo.name}', photo)
                    request.session['photo_path'] = file_name

                if send_otp_email(email, otp):
                    request.session["otp"] = otp
                    request.session["otp_timestamp"] = time.time()
                    request.session["otp_resend_attempts"] = 0
                    messages.success(request, "OTP sent to your email successfully!")
                    return render(request, "signup.html", {"otp_sent": True})

                messages.error(request, "Failed to send OTP. Please try again.")

    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})

def resend_otp(request):
    if not request.session.get("signup_data"):
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("signup")

    resend_attempts = request.session.get("otp_resend_attempts", 0)
    if resend_attempts >= OTP_RESEND_LIMIT:
        messages.error(request, "Maximum OTP resend attempts reached.")
        return render(request, "signup.html", {"otp_sent": True})

    email = request.session["signup_data"]["email"]
    otp = generate_otp()  # Generate new OTP

    if send_otp_email(email, otp):
        request.session["otp"] = otp
        request.session["otp_timestamp"] = time.time()
        request.session["otp_resend_attempts"] = resend_attempts + 1
        messages.success(request, "OTP resent successfully!")
    else:
        messages.error(request, "Failed to resend OTP. Try again.")

    return render(request, "signup.html", {"otp_sent": True, "otp_resend_attempts": resend_attempts + 1})

# Login View (Using Email as Login ID)
def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        try:
            user = Employee.objects.get(email=email)
            if check_password(password, user.password):
                # Create a session for the user (alternative to using django's auth system)
                request.session['user_id'] = user.employee_id
                request.session['user_name'] = user.full_name
                request.session['user_role'] = user.role

                return redirect_based_on_role(user)
            else:
                messages.error(request, "Invalid password.")
        except Employee.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, "login.html", {"form": form})

# Logout View
def logout_view(request):
    request.session.flush()
    return redirect("login")

# Redirect Based on Role
def redirect_based_on_role(user):
    if user.role == "Admin":
        return redirect("adminDashboard")
    elif user.role == "Inventory Manager":
        return redirect("inventoryManagerDashboard")
    elif user.role == "Sales Executive":
        return redirect("salesExecutiveDashboard")
    else:
        return redirect("login")

def adminDashboard(request):
    return render(request, 'AdminDashboard.html')