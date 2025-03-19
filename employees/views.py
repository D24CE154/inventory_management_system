import datetime
import time
import random

from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.timezone import now,timedelta
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Employee
from .forms import SignupForm, LoginForm, ForgotPassword,ResetPasswordForm
from django.contrib.auth.models import User
from django.core.files import File
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q

OTP_EXPIRY_SECONDS = 300
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
    if not is_active_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    if request.method == "POST" and "otp" in request.POST:
        entered_otp = request.POST.get("otp")

        if not request.session.get("signup_data"):
            messages.error(request, "Session expired. Please sign up again.")
            return redirect("signup")

        stored_otp = request.session.get("otp")
        otp_timestamp = request.session.get("otp_timestamp", 0)

        if time.time() - otp_timestamp > OTP_EXPIRY_SECONDS:
            messages.error(request, "OTP has expired. Request a new one.")
            return render(request, "add_employee.html", {"otp_sent": True, "otp_expired": True})

        if entered_otp != stored_otp:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, "add_employee.html", {"otp_sent": True})

        signup_data = request.session.get("signup_data")

        try:
            user = User.objects.create_user(
                username=signup_data["email"],
                email=signup_data["email"],
                password=signup_data["password"],
                is_active=True
            )
            user.save()

            employee = Employee(
                user=user,
                full_name=signup_data["full_name"],
                phone=signup_data["phone"],
                role=signup_data['role'],
                address=signup_data["address"],
                is_active=True
            )

            if "photo_path" in request.session:
                photo_path = request.session["photo_path"]
                with default_storage.open(photo_path, "rb") as photo_file:
                    employee.photo.save(photo_path, File(photo_file))

            employee.save()
            for key in ['signup_data', 'otp', 'otp_timestamp', 'otp_resend_attempts', 'photo_path']:
                if key in request.session:
                    del request.session[key]

            messages.success(request, f"Employee {signup_data['full_name']} added successfully!")
            return redirect("employee_management")

        except Exception as e:
            messages.error(request, f"Error during signup: {e}")
            return redirect("add_employee")

    return redirect("add_employee")

@login_required(login_url='login')
def add_employee(request):
    if not is_active_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

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
                "role": form.cleaned_data["role"],
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
                return render(request, "add_employee.html", {"otp_sent": True})

            messages.error(request, "Failed to send OTP. Please try again.")
        else:
            messages.error(request, "Form submission failed. Please correct the errors below.")

        return render(request, "add_employee.html", {"form": form})

    return render(request, "add_employee.html", {"form": SignupForm()})

@login_required(login_url='login')
def employee_management(request):
    # Check if user is admin
    if not is_active_admin(request.user):
        messages.error("You are not authorized to access this page")
        return redirect("error_403_view")

    search_query = request.GET.get('search', '')
    if search_query:
        employees = Employee.objects.filter(
            Q(full_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(role__icontains=search_query)
        ).order_by('-is_active', 'full_name')
    else:
        employees = Employee.objects.all().order_by('-is_active', 'full_name')

    role_counts = {
        'Admin':Employee.objects.filter(role='Admin').count(),
        'Inventory Manager':Employee.objects.filter(role='Inventory Manager').count(),
        'Sales Executive':Employee.objects.filter(role='Sales Executive').count(),
    }
    context = {
        'employees': employees,
        'role_counts': role_counts,
        'search_query': search_query,
    }
    return render(request, "employee_management.html", context)

def resend_otp(request):
    if not request.session.get("signup_data"):
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("signup")

    resend_attempts = request.session.get("otp_resend_attempts", 0)
    if resend_attempts >= OTP_RESEND_LIMIT:
        messages.error(request, "Maximum OTP resend attempts reached.")
        return render(request, "add_employee.html", {"otp_sent": True})

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

    return render(request, 'add_employee.html', {"otp_sent": True, "otp_resend_attempts": resend_attempts + 1})

def login_view(request):
    login_form = LoginForm(request.POST or None)

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

                    # Check if employee is active
                    if not employee.is_active:
                        messages.error(request, "Your employee account has been deactivated. Please contact an administrator.")
                        return render(request, "login.html", {"login_form": login_form})

                    user.last_login = now()
                    user.save(update_fields=["last_login"])

                    request.session["email"] = user.email
                    request.session["full_name"] = employee.full_name
                    request.session["photo"] = employee.photo.url if employee.photo else None

                except Employee.DoesNotExist:
                    messages.error(request, "Employee does not exist.")
                    return render(request, "login.html", {"login_form": login_form})

                login(request, user)
                return redirect_based_on_role(request)
            else:
                messages.error(request, "Account not activated. Please verify your email.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html", {"login_form": login_form})

def forgot_password_view(request):
    if request.method == 'POST':
        forgot_password_form = ForgotPassword(request.POST)
        if forgot_password_form.is_valid():
            email = forgot_password_form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
                employee = Employee.objects.get(user=user)  # Get Employee profile

                # Check if a reset request was made within the last hour
                if employee.last_password_reset and (now() - employee.last_password_reset) < timedelta(hours=1):
                    print("\n✅ DEBUG: Resending the same password reset link.")  # 🔥 Debugging
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_link = request.build_absolute_uri(reverse("reset_password", args=[uid, token]))

                else:
                    print("\n✅ DEBUG: Generating a new password reset link.")  # 🔥 Debugging
                    # Generate new reset link
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_link = request.build_absolute_uri(reverse("reset_password", args=[uid, token]))

                    # Update last password reset timestamp
                    employee.last_password_reset = now()
                    employee.save()

                # Send reset email
                send_mail(
                    "Password Reset Request",
                    f"Click the link to reset your password: {reset_link}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, "Password reset email sent!")
                return redirect("login")

            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")
                return redirect("forgot_password")

    else:
        forgot_password_form = ForgotPassword()

    return render(request, 'forgot_password.html', {'form': forgot_password_form})

def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            messages.error(request, "Invalid or expired reset link.")
            return redirect("forgot_password")

    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Invalid reset request.")
        return redirect("forgot_password")

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["password"])  # ✅ Secure password hashing
            user.save()
            messages.success(request, "Password reset successful! Please log in.")
            return redirect("login")
    else:
        form = ResetPasswordForm()

    return render(request, "reset-password.html", {"form": form})

def logout_view(request):
    logout(request)
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect("/login/?logged_out=True")

@login_required(login_url='login')
@login_required(login_url='login')
def redirect_based_on_role(request):
    try:
        employee = Employee.objects.get(user=request.user)

        # Ensure both user and employee are active
        if not employee.is_active or not request.user.is_active:
            messages.error(request, "Your account is inactive. Please contact an administrator.")
            logout(request)
            return redirect("login")

        if employee.role == "Admin":
            return redirect("adminDashboard")
        elif employee.role == "Inventory Manager":
            return redirect("inventoryManagerDashboard")
        elif employee.role == "Sales Executive":
            return redirect("salesExecutiveDashboard")
        else:
            messages.error(request, "Unauthorized access.")
            return redirect("error_403")
    except Employee.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect("error_404")

def error_404_view(request,exception=404):
    return render(request, 'errors/404.html', status=404)

def error_403_view(request,exception=403):
    return render(request, 'errors/403.html', status=403)

def error_500_view(request,exception=500):
    context = {
        'timestamp': datetime.datetime.now(),
    }
    return render(request, 'errors/500.html', context, status=500)

@login_required(login_url=settings.LOGIN_URL)
def adminDashboard(request):
    if not is_active_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")
    return render(request, 'admin_dashboard.html')

def is_active_admin(user):
    if user.is_authenticated and user.employee.role == 'Admin' and user.employee.is_active:
        return True
    return False

@login_required(login_url='login')
def toggle_employee_status(request,employee_id):
    if not is_active_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    if request.method != "POST":
        return redirect("employee_management")

    try:
        employee = Employee.obects.filter(id = employee_id)
        if employee.user == request.user:
            messages.error(request, "You cannot deactivate your own account.")
            return redirect("employee_management")

        action = request.POST.get("action")
        if action == "activate":
            employee.is_active = True
            employee.user.is_active = True
            messages.success(request, f"{employee.full_name} has been activated.")

        elif action == "deactivate":
            employee.is_active = False
            employee.user.is_active = False
            messages.success(request, f"{employee.full_name} has been deactivated.")

        employee.save()
        employee.user.save()

    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
    return redirect("employee_management")


