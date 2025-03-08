from django.urls import path, include
from .views import salesExecutiveDashboard

urlpatterns = [
    path("salesExecutiveDashboard/",salesExecutiveDashboard, name="salesExecutiveDashboard"),
]