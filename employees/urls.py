from django.urls import path, include

from .forms import ForgotPassword
from .views import (add_employee,employee_management, login_view, logout_view, redirect_based_on_role, adminDashboard,
                    resend_otp, verify_otp, forgot_password_view, reset_password_view,toggle_employee_status)

urlpatterns = [
   # path("signup/", add_employee, name="signup"),
    path('employee-management/', employee_management, name='employee_management'),
    path('employee-management/add/', add_employee, name='add_employee'),
    path('employee-management/toggle/<int:employee_id>/', toggle_employee_status, name='toggle_employee_status'),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('',login_view, name="login"),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('adminDashboard/', adminDashboard, name="adminDashboard"),
    path("redirect-based-on-role/", redirect_based_on_role, name="redirect_based_on_role"),
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("reset-password/<uidb64>/<token>/", reset_password_view, name="reset_password"),

]