from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('inventoryManagerDashboard/', views.inventoryManagerDashboard, name='inventoryManagerDashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_create, name='brand_create'),
    path('brands/<int:pk>/edit/', views.brand_update, name='brand_update'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),

    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    path('products/<int:pk>/stock/', views.product_stock, name='product_stock'),
    path('products/<int:product_pk>/stock/add/', views.stock_add, name='stock_add'),
    path('stock/<int:pk>/edit/', views.stock_edit, name='stock_edit'),
    path('stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('api/get-brands/', views.get_brands_by_category, name='get_brands_by_category'),
    path('products/<int:pk>/stock/template/download/', views.download_excel_template, name='download_excel_template'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)