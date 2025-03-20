import os

from django.conf.urls.static import static
from django.urls import path, include

from inventory_management_system import settings
from .forms import ForgotPassword
from .views import (add_employee,employee_management, login_view, logout_view, redirect_based_on_role, adminDashboard,
                    resend_otp, verify_otp, forgot_password_view, reset_password_view,toggle_employee_status)

urlpatterns = [
   # path("signup/", add_employee, name="signup"),
    path('employee-management/', employee_management, name='employee_management'),
    path('employee-management/add-employee/', add_employee, name='add_employee'),
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

if settings.DEBUG:
    # Serve media files during development
    if hasattr(settings, 'MEDIA_ROOT') and hasattr(settings, 'MEDIA_URL'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Serve static files during development
    if hasattr(settings, 'STATIC_URL'):
        # Check if STATIC_ROOT exists before using it
        if hasattr(settings, 'STATIC_ROOT'):
            urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        # Else use STATICFILES_DIRS if defined
        elif hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

    # Serve profile pics directly
    profile_pics_dir = os.path.join(settings.BASE_DIR, 'profile_pics')
    if os.path.exists(profile_pics_dir):
        urlpatterns += static('/profile_pics/', document_root=profile_pics_dir)