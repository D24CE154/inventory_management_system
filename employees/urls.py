from django.urls import path, include
from .views import signup_view, login_view, logout_view,redirect_based_on_role

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("accounts/", include("allauth.urls")),
    path('',login_view, name="login"),
    path("redirect-based-on-role/", redirect_based_on_role, name="redirect_based_on_role"),
]