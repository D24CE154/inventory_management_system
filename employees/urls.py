import os

from django.conf.urls.static import static
from django.urls import path, include

from .views import (add_employee, employee_management, login_view, logout_view, redirect_based_on_role, adminDashboard,
                    resend_otp, verify_otp, forgot_password_view, reset_password_view, view_employee_details
, edit_employee, error_404_view, error_500_view, error_403_view,delete_employee)

urlpatterns = [
   # path("signup/", add_employee, name="signup"),
    path('employee-management/', employee_management, name='employee_management'),
    path('employee-management/add-employee/', add_employee, name='add_employee'),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('',login_view, name="login"),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('adminDashboard/', adminDashboard, name="adminDashboard"),
    path("redirect-based-on-role/", redirect_based_on_role, name="redirect_based_on_role"),
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("reset-password/<uidb64>/<token>/", reset_password_view, name="reset_password"),
    path('employee-management/<int:employee_id>/details/', view_employee_details, name='employee_details'),
    path('employee-management/<int:employee_id>/edit/', edit_employee, name='edit_employee'),
    path('delete/<int:employee_id>/', delete_employee, name='delete_employee'),
    path('error_404/', error_404_view,name='error_404_view'),
    path('error_500',error_500_view,name='error_500_view'),
    path('error_403',error_403_view,name='error_403_view')

]
