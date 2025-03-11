import time
import random
from django.contrib.auth import login,logout
from django.utils.timezone import now
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Employee
from .forms import SignupForm, LoginForm
from django.contrib.auth.models import User
from django.core.files import File

OTP_EXPIRY_SECONDS = 300  # 5 minutes expiry
OTP_RESEND_LIMIT = 3

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
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


def verify_otp(request):
    if request.method == "POST" and "otp" in request.POST:
        entered_otp = request.POST.get("otp")

        if not request.session.get("signup_data"):
            messages.error(request, "Session expired. Please sign up again.")
            return redirect("signup")

        stored_otp = request.session.get("otp")
        otp_timestamp = request.session.get("otp_timestamp", 0)

        if time.time() - otp_timestamp > OTP_EXPIRY_SECONDS:
            messages.error(request, "OTP has expired. Request a new one.")
            return render(request, "signup.html", {"otp_sent": True, "otp_expired": True})

        if entered_otp != stored_otp:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, "signup.html", {"otp_sent": True})

        signup_data = request.session.get("signup_data")

        try:
            # Create and Save User
            user = User.objects.create_user(
                username=signup_data["email"],
                email=signup_data["email"],
                password=signup_data["password"],  # Django automatically hashes it
                is_active=True
            )
            user.save()

            # Create Employee instance linked to User
            employee = Employee(
                user=user,
                full_name=signup_data["full_name"],
                phone=signup_data["phone"],
                role="Sales Executive",
                address=signup_data["address"],
                is_active=True
            )

            # Assign saved photo if available
            if "photo_path" in request.session:
                photo_path = request.session["photo_path"]
                with default_storage.open(photo_path, "rb") as photo_file:
                    employee.photo.save(photo_path, File(photo_file))

            employee.save()

            request.session.flush()
            messages.success(request, "Signup successful! Please log in.")
            return redirect("login")

        except Exception as e:
            messages.error(request, f"Error during signup: {e}")
            return redirect("signup")

    return redirect("signup")

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]
            otp = generate_otp()

            request.session["signup_data"] = {
                "full_name": form.cleaned_data["full_name"],
                "email": email,
                "phone": form.cleaned_data["phone"],
                "address": form.cleaned_data["address"],
                "password": form.cleaned_data["password"],
            }

            if "photo" in request.FILES:
                photo = request.FILES["photo"]
                file_name = default_storage.save(f'profile_pics/{form.cleaned_data["phone"]}_pfp.jpg', photo)
                request.session["photo_path"] = file_name

            request.session["otp"] = otp
            request.session["otp_timestamp"] = time.time()
            request.session["otp_resend_attempts"] = 0

            if send_otp_email(email, otp):
                messages.success(request, "OTP sent to your email successfully!")
                return render(request, "signup.html", {"otp_sent": True})

            messages.error(request, "Failed to send OTP. Please try again.")
        else:
            print("\n🔹 DEBUG: Form validation errors:", form.errors)  # 🔥 Debugging line
            messages.error(request, "Form submission failed. Please correct the errors below.")

        return render(request, "signup.html", {"form": form})

    return render(request, "signup.html", {"form": SignupForm()})


def resend_otp(request):
    if not request.session.get("signup_data"):
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("signup")

    resend_attempts = request.session.get("otp_resend_attempts", 0)
    if resend_attempts >= OTP_RESEND_LIMIT:
        messages.error(request, "Maximum OTP resend attempts reached.")
        return render(request, "signup.html", {"otp_sent": True})

    email = request.session["signup_data"]["email"]
    current_time = time.time()
    otp_expiry = request.session.get("otp_timestamp", 0) + OTP_EXPIRY_SECONDS

    if current_time < otp_expiry:
        otp = request.session["otp"]
        remaining_time = int(otp_expiry - current_time)
    else:
        otp = generate_otp()
        request.session["otp"] = otp
        request.session["otp_timestamp"] = current_time
        remaining_time = OTP_EXPIRY_SECONDS

    if send_otp_email(email, otp):
        request.session["otp_resend_attempts"] = resend_attempts + 1
        messages.success(request, f"OTP resent successfully! It is valid for {remaining_time // 60} min {remaining_time % 60} sec.")
    else:
        messages.error(request, "Failed to resend OTP. Try again.")

    return render(request, 'signup.html', {"otp_sent": True, "otp_resend_attempts": resend_attempts + 1})

# Login View (Using Email as Login ID)
def login_view(request):
    login_form = LoginForm(request.POST or None)  # Ensure form is always available

    if request.method == "POST" and login_form.is_valid():
        email = login_form.cleaned_data["email"]
        password = login_form.cleaned_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return render(request, "login.html", {"login_form": login_form})

        if user and user.check_password(password):
            if user.is_active:
                try:

                    employee = Employee.objects.get(user=user)
                    user.last_login = now()
                    user.save(update_fields=["last_login"])

                    request.session["email"] = user.email
                    request.session["full_name"] = employee.full_name
                    request.session["photo"] = employee.photo.url if employee.photo else None
                except Employee.DoesNotExist:
                    messages.error(request, "Employee does not exist.")
                    return render(request, "signup.html", {"signup_form": SignupForm()})

                login(request, user)
                return redirect_based_on_role(employee)
            else:
                messages.error(request, "Account not activated. Please verify your email.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html", {"login_form": login_form})

# Logout View
def logout_view(request):
    logout(request)
    request.session.flush()
    response = redirect("login")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response

# Redirect Based on Role
def redirect_based_on_role(employee):

    if employee.role == "Admin":
        return redirect("adminDashboard")
    elif employee.role == "Inventory Manager":
        return redirect("inventoryManagerDashboard")
    elif employee.role == "Sales Executive":
        return redirect("salesExecutiveDashboard")
    else:
        return redirect("login")

def adminDashboard(request):
    return render(request, 'AdminDashboard.html')