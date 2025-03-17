"""
URL configuration for inventory_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path ,include
import employees.urls
from employees.views import error_403_view,error_404_view,error_500_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('employees/', include('employees.urls')),
    path('',include(employees.urls)),
    path('inventory/',include('inventory.urls')),
    path('pos/',include('pos.urls')),
    path('supplier/',include('supplier.urls')),
]

handler404 = 'employees.views.error_404_view'
handler403 = 'employees.views.error_403_view'
handler500 = 'employees.views.error_500_view'