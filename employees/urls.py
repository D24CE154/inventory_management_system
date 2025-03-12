from django.urls import path, include

from .forms import ForgotPassword
from .views import (signup_view, login_view, logout_view,redirect_based_on_role, adminDashboard,
                    resend_otp,verify_otp, forgot_password_view, reset_password_view)

urlpatterns = [
    path("signup/", signup_view, name="signup"),
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