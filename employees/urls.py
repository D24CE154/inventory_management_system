from django.urls import path, include
from .views import signup_view, login_view, logout_view,redirect_based_on_role, adminDashboard, resend_otp,verify_otp

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('',login_view, name="login"),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('adminDashboard/', adminDashboard, name="adminDashboard"),
    path("redirect-based-on-role/", redirect_based_on_role, name="redirect_based_on_role"),
]