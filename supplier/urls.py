from django.urls import path, include

from .views import supplierDashboard
urlpatterns = [
    path("supplierDashboard/", supplierDashboard, name="supplierDashboard"),
]