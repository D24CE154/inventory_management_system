from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('inventoryManagerDashboard/', views.inventoryManagerDashboard, name='inventoryManagerDashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add_category/', views.add_category, name='add_category'),
    path('categories/edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('categories/<int:category_id>/products/', views.category_products, name='category_products'),
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.add_brand, name='add_brand'),
    path('brands/edit/<int:brand_id>/', views.edit_brand, name='edit_brand'),
    path('brands/delete/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('products/<int:product_id>/items/', views.product_items_list, name='product_items_list'),
    path('products/add_product_items/<int:product_id>/<int:stock>/', views.add_product_items, name='add_product_items'),
    path('product_items/edit/<int:item_id>/', views.edit_product_item, name='edit_product_item'),
    path('product_items/delete/<int:item_id>/', views.delete_product_item, name='delete_product_item'),
    path('get_brands_by_category/<int:category_id>/', views.get_brands_by_category, name='get_brands_by_category'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)