from django.urls import path, include
from .views import inventoryManagerDashboard

urlpatterns = [
    path("inventoryManagerDashboard/", inventoryManagerDashboard, name="inventoryManagerDashboard"),
]