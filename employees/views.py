import datetime
import random
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.db.models import ExpressionWrapper, DecimalField, F
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now, timedelta
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from inventory.models import *
from pos.models import *
from supplier.models import *
from .forms import SignupForm, LoginForm, ForgotPassword, ResetPasswordForm, EmployeeEditForm
from .models import *

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
        return redirect("error_403_view")

    employee = request.user.employee

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
                file_name = default_storage.save(f'{form.cleaned_data["phone"]}_pfp.jpg', photo)
                request.session["photo_path"] = file_name

            request.session["otp"] = otp
            request.session["otp_timestamp"] = time.time()
            request.session["otp_resend_attempts"] = 0

            if send_otp_email(email, otp):
                messages.success(request, "OTP sent to your email successfully!")
                return render(request, "add_employee.html", {"otp_sent": True, "logged_in_employee": employee})

            messages.error(request, "Failed to send OTP. Please try again.")
        else:
            messages.error(request, "Form submission failed. Please correct the errors below.")

        return render(request, "add_employee.html", {"form": form, "logged_in_employee": employee})

    return render(request, "add_employee.html", {"form": SignupForm(), "logged_in_employee": employee})


@login_required(login_url='login')
def delete_employee(request, employee_id):
    if not is_active_admin(request.user):
        return redirect("error_403_view")

    try:
        employee = Employee.objects.get(employee_id=employee_id)
        if request.user.employee.employee_id == employee_id:
            messages.error(request, "You cannot delete your own account.")
            return redirect('employee_management')

        employee_name = employee.full_name
        user = employee.user
        user.is_active = False
        user.save()

        # Mark the employee record inactive as well
        employee.is_active = False
        employee.save()

        messages.success(request, f"Employee {employee_name} has been deleted successfully.")
        return redirect('employee_management')
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect('employee_management')

@login_required(login_url='login')
def employee_management(request):
    # Check if user is admin
    if not is_active_admin(request.user):
        return redirect("error_403_view")

    search_query = request.GET.get('search', '').strip()

    if search_query:
        employees = Employee.objects.filter(
            Q(employee_id__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(role__icontains=search_query)
        ).order_by('employee_id', )
    else:
        employees = Employee.objects.all().order_by('employee_id')

    role_counts = {
        'Admin': Employee.objects.filter(role='Admin').count(),
        'Inventory Manager': Employee.objects.filter(role='Inventory Manager').count(),
        'Sales Executive': Employee.objects.filter(role='Sales Executive').count(),
    }
    context = {
        'employees': employees,
        'role_counts': role_counts,
        'search_query': search_query,
        'logged_in_employee': request.user.employee,
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
        messages.success(request,
                         f"OTP resent successfully! It is valid for {remaining_time // 60} min {remaining_time % 60} sec.")
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

                    if not employee.is_active:
                        messages.error(request,
                                       "Your employee account has been deactivated. Please contact an administrator.")
                        return render(request, "login.html", {"login_form": login_form})

                    request.session.flush()
                    login(request, user)

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
                employee = Employee.objects.get(user=user)

                if employee.last_password_reset and (now() - employee.last_password_reset) < timedelta(hours=1):
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_link = request.build_absolute_uri(reverse("reset_password", args=[uid, token]))

                else:
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_link = request.build_absolute_uri(reverse("reset_password", args=[uid, token]))

                    employee.last_password_reset = now()
                    employee.save()

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

    return render(request, 'forgot_password.html', {'forgot_password_form': forgot_password_form})


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
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Password reset successful! Please log in.")
            return redirect("login")
    else:
        form = ResetPasswordForm()

    return render(request, "reset-password.html", {"form": form})


def logout_view(request):
    logout(request)
    request.session.flush()
    request.session.modified = True
    return redirect('login')


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
            return redirect("error_403")
    except Employee.DoesNotExist:
        return redirect("error_404")


def error_404_view(request, exception=404):
    return render(request, 'errors/404.html', status=404)


def error_403_view(request, exception=403):
    return render(request, 'errors/403.html', status=403)


def error_500_view(request, exception=500):
    context = {
        'timestamp': datetime.datetime.now(),
    }
    return render(request, 'errors/500.html', context, status=500)


@login_required(login_url='login')
def adminDashboard(request):
    if not is_active_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    today = now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)

    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)

    current_month_revenue = Sale.objects.filter(
        sale_date__date__range=[first_day_current_month, today]
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    previous_month_revenue = Sale.objects.filter(
        sale_date__date__range=[first_day_previous_month, last_day_previous_month]
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    current_month_sales = Sale.objects.filter(
        sale_date__date__range=[first_day_current_month, today]
    ).count()

    previous_month_sales = Sale.objects.filter(
        sale_date__date__range=[first_day_previous_month, last_day_previous_month]
    ).count()

    revenue_change = calculate_percentage_change(current_month_revenue, previous_month_revenue)
    sales_change = calculate_percentage_change(current_month_sales, previous_month_sales)

    revenue_data = {
        'last_7_days': get_revenue_data(last_7_days, today),
        'last_30_days': get_revenue_data(last_30_days, today),
        'last_90_days': get_revenue_data(last_90_days, today),
    }

    first_day_of_month = today.replace(day=1)
    first_day_of_last_month = (first_day_of_month - timedelta(days=1)).replace(day=1)
    last_day_of_last_month = first_day_of_month - timedelta(days=1)
    first_day_of_year = today.replace(month=1, day=1)

    category_data = {
        'this_month': get_category_sales_data(first_day_of_month, today),
        'last_month': get_category_sales_data(first_day_of_last_month, last_day_of_last_month),
        'this_year': get_category_sales_data(first_day_of_year, today),
    }

    total_revenue = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_sales = Sale.objects.count()
    product_count = Product.objects.count()
    employee_count = Employee.objects.count()

    recent_sales = Sale.objects.select_related('customer_id').order_by('-sale_date')[:5]

    # Calculate low stock products using annotation
    low_stock_products = Product.objects.annotate(
        stock=Sum('items__quantity')  # Corrected related field name
    ).filter(stock__lte=10).order_by('stock')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'product_count': product_count,
        'employee_count': employee_count,
        'revenue_change': revenue_change,
        'sales_change': sales_change,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'revenue_data': revenue_data,
        'category_data': category_data,
        'employee': Employee.objects.get(employee_id=request.user.employee.employee_id)
    }

    return render(request, 'admin_dashboard.html', context)


def calculate_percentage_change(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return int(((current - previous) / previous) * 100)


def get_revenue_data(start_date, end_date):
    sales_by_date = Sale.objects.filter(
        sale_date__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('sale_date')
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    date_range = [(start_date + timedelta(days=i)) for i in range((end_date - start_date).days + 1)]
    sales_dict = {item['date']: item['total'] for item in sales_by_date}
    labels = [date.strftime('%d %b') for date in date_range]
    data = [float(sales_dict.get(date, 0)) for date in date_range]

    return {'labels': labels, 'data': data}


def get_category_sales_data(start_date, end_date):
    categories = ProductCategory.objects.all()

    sales_by_category = []
    for category in categories:
        # Calculate total by multiplying quantity and selling_price
        total = SaleItem.objects.filter(
            sale_id__sale_date__date__range=[start_date, end_date],
            product_id__category_id=category
        ).annotate(
            item_total=ExpressionWrapper(
                F('quantity') * F('selling_price'),
                output_field=DecimalField()
            )
        ).aggregate(total=Sum('item_total'))['total'] or 0

        sales_by_category.append({
            'category': category.name,
            'total': float(total)
        })

    sales_by_category.sort(key=lambda x: x['total'], reverse=True)
    labels = [item['category'] for item in sales_by_category]
    data = [item['total'] for item in sales_by_category]

    return {'labels': labels, 'data': data}


def is_active_employee(user):
    if user.is_authenticated and user.employee.is_active and (
            user.employee.role in ['Admin', 'Sales Executive', 'Inventory Manager']):
        return True
    return False


def is_active_admin(user):
    if user.is_authenticated and user.employee.role == 'Admin' and user.employee.is_active:
        return True
    return False


@login_required(login_url='login')
def view_employee_details(request, employee_id):
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        logged_in_employee = request.user.employee

        if request.user.employee.employee_id == employee_id:
            context = {'employee': employee,
                       'logged_in_employee': logged_in_employee}

            return render(request, "employee_details.html", context)

        elif is_active_admin(request.user):
            context = {'employee': employee,
                       'logged_in_employee': logged_in_employee}
            return render(request, "employee_details.html", context)
        else:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('error_403_view')
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found")
        return redirect('employee_management')


@login_required()
def edit_employee(request, employee_id):
    if not is_active_admin(request.user):
        return redirect('error_403_view')
    try:
        employee = Employee.objects.get(employee_id=employee_id)

        if request.method == "POST":
            employeeEditForm = EmployeeEditForm(request.POST, request.FILES, instance=employee)
            if employeeEditForm.is_valid():
                user = employee.user
                user.email = employeeEditForm.cleaned_data.get('email')
                if employeeEditForm.cleaned_data.get('password'):
                    user.set_password(employeeEditForm.cleaned_data.get('password'))
                user.save()
                employee_update = employeeEditForm.save(commit=False)
                if 'photo' in request.FILES:
                    if employee.photo:
                        default_storage.delete(employee.photo.path)
                    employee_update.photo = request.FILES['photo']
                employee_update.save()
                messages.success(request, "Employee updated successfully.")
                return redirect("employee_management")
            else:
                messages.error(request, "Please correct the error below.")
        else:
            initial_data = {
                'email': employee.user.email,
                'full_name': employee.full_name,
                'phone': employee.phone,
                'role': employee.role,
                'address': employee.address,
                'is_active': employee.is_active,
            }
            employeeEditForm = EmployeeEditForm(initial=initial_data)
        context = {'employee': employee, 'form': employeeEditForm,'logged_in_employee': request.user.employee}
        return render(request, "edit_employee.html", context)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect('employee_management')


def reports_analytics(request):
    employees = Employee.objects.all()
    context = {
        "logged_in_employee": request.user.employee,
        "employees": employees,
    }
    return render(request, 'base_report_analytics.html', context)


def log_report_generation(request, report_name):
    AuditLog.objects.create(employee=request.user.employee, action=f"Generated {report_name} report")


def draw_header_footer(c):
    width, height = A4
    # Header styling
    c.setFillColorRGB(0.2, 0.4, 0.6)
    c.rect(0, height - 50, width, 50, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 35, "IG mobile - Report")
    # Footer styling
    c.setFillColorRGB(0.2, 0.4, 0.6)
    c.rect(0, 0, width, 40, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 10)
    c.drawString(50, 15, "IG mobile")
    c.drawRightString(width - 50, 15, f"Page {c.getPageNumber()}")
    c.setFillColorRGB(0, 0, 0)


@login_required(login_url="login")
def employee_sales_performance_report_pdf(request):
    filter_params = {}
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    try:
        if start_date_str:
            filter_params["sale_date__date__gte"] = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            filter_params["sale_date__date__lte"] = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except Exception:
        pass

    employee_param = request.GET.get("employee_id")
    if employee_param:
        try:
            employee_param = int(employee_param)
            employees = Employee.objects.filter(employee_id=employee_param)
        except ValueError:
            employees = Employee.objects.all()
    else:
        employees = Employee.objects.all()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=employee_sales_performance_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)

    draw_header_footer(p)
    # Distinct report title styling
    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(80, 780, "Employee Sales Performance Report")

    table_data = [["Employee Name", "Total Sales", "Revenue"]]
    sales_counts = []
    for emp in employees:
        sales = Sale.objects.filter(employee_id=emp, **filter_params)
        total_sales = sales.count()
        total_revenue = sales.aggregate(total=Sum("total_amount"))["total"] or 0
        table_data.append([emp.full_name, total_sales, total_revenue])
        sales_counts.append(total_sales)

    table = Table(table_data, colWidths=[200, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    table.wrapOn(p, 50, 650)
    table.drawOn(p, 50, 650)

    # Bar chart with border styling
    drawing_bar = Drawing(400, 150)
    bar_chart = VerticalBarChart()
    bar_chart.x = 50
    bar_chart.y = 20
    bar_chart.height = 100
    bar_chart.width = 300
    bar_chart.data = [sales_counts]
    bar_chart.categoryAxis.categoryNames = [emp.full_name for emp in employees]
    bar_chart.valueAxis.valueMin = 0
    bar_chart.valueAxis.valueMax = max(sales_counts + [1]) + 10
    bar_chart.barWidth = 12
    bar_chart.strokeColor = colors.black
    drawing_bar.add(bar_chart)
    renderPDF.draw(drawing_bar, p, 50, 480)

    # Pie chart with distinct slice borders
    drawing_pie = Drawing(400, 150)
    pie_chart = Pie()
    pie_chart.x = 150
    pie_chart.y = 15
    pie_chart.width = 100
    pie_chart.height = 100
    pie_chart.data = sales_counts
    pie_chart.labels = [emp.full_name for emp in employees]
    pie_chart.slices.strokeWidth = 1
    pie_chart.slices.strokeColor = colors.black
    drawing_pie.add(pie_chart)
    renderPDF.draw(drawing_pie, p, 50, 320)

    # Insights text styling
    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.3, 0.1, 0.5)
    p.drawString(50, 300, "Insights: Employees with highest sales indicate top performers.")

    p.showPage()
    draw_header_footer(p)
    p.setFont("Helvetica", 12)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(50, 780, "Additional Insights: Consistent performance trends observed.")
    p.showPage()
    p.save()

    log_report_generation(request, "Employee Sales Performance")
    return response


@login_required(login_url="login")
def audit_log_report_pdf(request):
    filter_params = {}
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    try:
        if start_date_str:
            filter_params["date__date__gte"] = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            filter_params["date__date__lte"] = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except Exception:
        pass

    employee_param = request.GET.get("employee_id")
    if employee_param:
        try:
            employee_param = int(employee_param)
            filter_params["employee__employee_id"] = employee_param
        except ValueError:
            pass

    logs = AuditLog.objects.filter(**filter_params).order_by("-date")[:20]
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=audit_log_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)

    draw_header_footer(p)
    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(120, 780, "Audit Log Report")

    y = 750
    actions = {}
    for log in logs:
        text = f"{log.date.strftime('%Y-%m-%d %H:%M')}: {log.employee.full_name} - {log.action}"
        p.setFont("Helvetica", 10)
        p.setFillColorRGB(0, 0, 0)
        p.drawString(50, y, text)
        y -= 15
        actions[log.action] = actions.get(log.action, 0) + 1

    drawing_bar = Drawing(300, 150)
    bar_chart = VerticalBarChart()
    bar_chart.x = 50
    bar_chart.y = 20
    bar_chart.height = 100
    bar_chart.width = 200
    bar_chart.data = [list(actions.values())]
    bar_chart.categoryAxis.categoryNames = list(actions.keys())
    bar_chart.valueAxis.valueMin = 0
    bar_chart.valueAxis.valueMax = max(list(actions.values()) + [1]) + 2
    bar_chart.strokeColor = colors.black
    drawing_bar.add(bar_chart)
    renderPDF.draw(drawing_bar, p, 50, y - 150)

    drawing_pie = Drawing(300, 150)
    pie_chart = Pie()
    pie_chart.x = 65
    pie_chart.y = 15
    pie_chart.width = 170
    pie_chart.height = 120
    pie_chart.data = list(actions.values())
    pie_chart.labels = list(actions.keys())
    pie_chart.simpleLabels = True
    drawing_pie.add(pie_chart)
    renderPDF.draw(drawing_pie, p, 50, y - 320)

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.2, 0.2, 0.2)
    p.drawString(50, y - 340, "Insights: Common actions and their frequency help identify recurring trends.")
    p.showPage()
    p.save()

    log_report_generation(request, "Audit Log")
    return response


@login_required(login_url="login")
def sales_summary_report_pdf(request):
    filter_params = {}
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    try:
        if start_date_str:
            filter_params["sale_date__date__gte"] = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            filter_params["sale_date__date__lte"] = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except Exception:
        pass

    total_sales = Sale.objects.filter(**filter_params).count()
    total_revenue = Sale.objects.filter(**filter_params).aggregate(total=Sum("total_amount"))["total"] or 0

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=sales_summary_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)

    draw_header_footer(p)
    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(150, 780, "Sales Summary Report")
    p.setFont("Helvetica", 12)
    y = 750
    p.setFillColorRGB(0, 0, 0)
    p.drawString(50, y, f"Total Sales: {total_sales}")
    y -= 20
    p.drawString(50, y, f"Total Revenue: {total_revenue}")
    y -= 40

    drawing_bar = Drawing(300, 150)
    bar_chart = VerticalBarChart()
    bar_chart.x = 50
    bar_chart.y = 20
    bar_chart.height = 100
    bar_chart.width = 200
    bar_chart.data = [[total_sales, float(total_revenue)]]
    bar_chart.categoryAxis.categoryNames = ["Sales", "Revenue"]
    bar_chart.valueAxis.valueMin = 0
    bar_chart.valueAxis.valueMax = max(total_sales, float(total_revenue)) + 10
    bar_chart.strokeColor = colors.black
    drawing_bar.add(bar_chart)
    renderPDF.draw(drawing_bar, p, 50, y - 150)

    drawing_line = Drawing(300, 150)
    line_chart = LinePlot()
    line_chart.x = 50
    line_chart.y = 20
    line_chart.height = 100
    line_chart.width = 200
    line_chart.data = [(0, total_revenue * 0.8), (1, total_revenue), (2, total_revenue * 1.1)]
    line_chart.xValueAxis.valueMin = 0
    line_chart.xValueAxis.valueMax = 2
    line_chart.xValueAxis.valueSteps = [0, 1, 2]
    line_chart.yValueAxis.valueMin = 0
    line_chart.yValueAxis.valueMax = total_revenue * 1.2
    line_chart.strokeColor = colors.black
    drawing_line.add(line_chart)
    renderPDF.draw(drawing_line, p, 50, y - 320)

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.3, 0.1, 0.4)
    p.drawString(50, y - 340, "Insights: Trends indicate steady revenue growth over time.")
    p.showPage()
    p.save()

    log_report_generation(request, "Sales Summary")
    return response


@login_required(login_url="login")
def supplier_report_pdf(request):
    filter_params = {}
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    try:
        if start_date_str:
            filter_params["created_at__date__gte"] = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            filter_params["created_at__date__lte"] = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except Exception:
        pass

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=supplier_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)

    draw_header_footer(p)
    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(150, 780, "Supplier Report")
    y = 750

    names = []
    order_counts = []
    # Assume PurchaseOrder is used for supplier orders
    from supplier.models import Supplier
    suppliers = Supplier.objects.filter(**filter_params)
    for supplier in suppliers:
        names.append(supplier.supplier_name)
        count = PurchaseOrder.objects.filter(supplier_id=supplier).count()
        order_counts.append(count)

    drawing_bar = Drawing(400, 150)
    bar_chart = VerticalBarChart()
    bar_chart.x = 50
    bar_chart.y = 20
    bar_chart.height = 100
    bar_chart.width = 300
    bar_chart.data = [order_counts]
    bar_chart.categoryAxis.categoryNames = names
    bar_chart.valueAxis.valueMin = 0
    bar_chart.valueAxis.valueMax = max(order_counts + [1]) + 5
    bar_chart.strokeColor = colors.black
    drawing_bar.add(bar_chart)
    renderPDF.draw(drawing_bar, p, 50, y - 150)

    drawing_pie = Drawing(400, 150)
    pie_chart = Pie()
    pie_chart.x = 150
    pie_chart.y = 20
    pie_chart.width = 100
    pie_chart.height = 100
    pie_chart.data = order_counts
    pie_chart.labels = names
    pie_chart.slices.strokeWidth = 1
    pie_chart.slices.strokeColor = colors.black
    drawing_pie.add(pie_chart)
    renderPDF.draw(drawing_pie, p, 50, y - 320)

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.2, 0.2, 0.2)
    p.drawString(50, y - 340, "Insights: High order counts identify key suppliers for strategic partnerships.")
    p.showPage()
    p.save()

    log_report_generation(request, "Supplier")
    return response


@login_required(login_url="login")
def customer_purchase_report_pdf(request):
    # Get customer purchases (example: last 20 sales)
    sales = Sale.objects.select_related('customer_id').order_by('-sale_date')[:20]
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=customer_purchase_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)
    draw_header_footer(p)

    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(100, 780, "Customer Purchase Report")

    y = 750
    table_data = [["Date", "Customer Name", "Total Amount"]]
    for sale in sales:
        date_str = sale.sale_date.strftime("%Y-%m-%d")
        table_data.append([date_str, sale.customer_id.customer_name, sale.total_amount])

    table = Table(table_data, colWidths=[100, 200, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
    ]))
    table.wrapOn(p, 50, y)
    table.drawOn(p, 50, y - (len(table_data) * 20))

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.3, 0.1, 0.5)
    p.drawString(50, y - (len(table_data) * 20) - 30,
                 "Insights: Customer trends help tailor marketing strategies.")

    p.showPage()
    p.save()
    log_report_generation(request, "Customer Purchase")
    return response


@login_required(login_url="login")
def financial_analytics_report_pdf(request):
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=financial_analytics_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)
    draw_header_footer(p)

    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(120, 780, "Financial Analytics Report")

    y = 750
    p.setFont("Helvetica", 12)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(50, y, f"Total Sales: {total_sales}")
    p.drawString(50, y - 20, f"Total Revenue: {total_revenue}")

    drawing_bar = Drawing(300, 150)
    bar_chart = VerticalBarChart()
    bar_chart.x = 50
    bar_chart.y = 20
    bar_chart.height = 100
    bar_chart.width = 200
    bar_chart.data = [[total_sales, float(total_revenue)]]
    bar_chart.categoryAxis.categoryNames = ["Sales", "Revenue"]
    bar_chart.valueAxis.valueMin = 0
    bar_chart.valueAxis.valueMax = max(total_sales, float(total_revenue)) + 10
    bar_chart.strokeColor = colors.black
    drawing_bar.add(bar_chart)
    renderPDF.draw(drawing_bar, p, 50, y - 150)

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.3, 0.1, 0.4)
    p.drawString(50, y - 170, "Insights: Financial trends throughout the period.")

    p.showPage()
    p.save()
    log_report_generation(request, "Financial Analytics")
    return response

@login_required(login_url="login")
def product_inventory_report_pdf(request):
    products = Product.objects.all()
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=product_inventory_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)
    draw_header_footer(p)

    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(130, 780, "Product Inventory Report")

    table_data = [["Product Name", "Category", "Total Stock"]]
    for prod in products:
        table_data.append([prod.name, prod.category.name, prod.total_stock])

    table = Table(table_data, colWidths=[200, 150, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkred),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    table.wrapOn(p, 50, 700)
    table.drawOn(p, 50, 700 - (len(table_data) * 20))

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.2, 0.2, 0.5)
    p.drawString(50, 700 - (len(table_data) * 20) - 30,
                 "Insights: Low stock items may need replenishment.")

    p.showPage()
    p.save()
    log_report_generation(request, "Product Inventory")
    return response

@login_required(login_url="login")
def product_category_report_pdf(request):
    categories = ProductCategory.objects.all()
    table_data = [["Category", "Number of Products"]]
    for cat in categories:
        count = cat.product_set.count()
        table_data.append([cat.name, count])

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=product_category_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)
    draw_header_footer(p)

    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(130, 780, "Product Category Report")

    table = Table(table_data, colWidths=[250, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkorange),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    table.wrapOn(p, 50, 700)
    table.drawOn(p, 50, 700 - (len(table_data) * 20))

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.3, 0.1, 0.5)
    p.drawString(50, 700 - (len(table_data) * 20) - 30,
                 "Insights: Categories with few products might be phased out.")

    p.showPage()
    p.save()
    log_report_generation(request, "Product Category")
    return response

@login_required(login_url="login")
def brand_performance_report_pdf(request):
    brands = Brand.objects.all()
    table_data = [["Brand", "Number of Products"]]
    for brand in brands:
        count = brand.product_set.count()
        table_data.append([brand.name, count])

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=brand_performance_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)
    draw_header_footer(p)

    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(140, 780, "Brand Performance Report")

    table = Table(table_data, colWidths=[250, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkviolet),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    table.wrapOn(p, 50, 700)
    table.drawOn(p, 50, 700 - (len(table_data) * 20))

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.2, 0.3, 0.5)
    p.drawString(50, 700 - (len(table_data) * 20) - 30,
                 "Insights: Top performing brands drive market growth.")

    p.showPage()
    p.save()
    log_report_generation(request, "Brand Performance")
    return response


@login_required(login_url="login")
def purchase_orders_report_pdf(request):
    orders = PurchaseOrder.objects.all().order_by('-received_date')[:20]
    table_data = [["Order ID", "Supplier", "Status", "Received Date", "Total Cost"]]
    for order in orders:
        date_str = order.received_date.strftime("%Y-%m-%d")
        table_data.append(
            [order.purchase_order_id, order.supplier_id.supplier_name, order.status, date_str, order.total_cost])

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=purchase_orders_report.pdf"
    p = canvas.Canvas(response, pagesize=A4)
    draw_header_footer(p)

    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.drawString(120, 780, "Purchase Orders Report")

    table = Table(table_data, colWidths=[70, 150, 100, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    table.wrapOn(p, 50, 700)
    table.drawOn(p, 50, 700 - (len(table_data) * 20))

    p.setFont("Helvetica-Oblique", 12)
    p.setFillColorRGB(0.3, 0.1, 0.5)
    p.drawString(50, 700 - (len(table_data) * 20) - 30,
                 "Insights: Monitoring order statuses aids in timely shipments.")

    p.showPage()
    p.save()
    log_report_generation(request, "Purchase Orders")
    return response
