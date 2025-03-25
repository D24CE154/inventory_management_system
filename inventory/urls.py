from django.urls import path, include
from .views import inventoryManagerDashboard, add_category, edit_category, delete_category, category_list

urlpatterns = [
    path("inventoryManagerDashboard/", inventoryManagerDashboard, name="inventoryManagerDashboard"),
    path('categories/',category_list,name='category_list'),
    path("categories/add_category/", add_category, name="add_category"),
    path('categories/edit_category/<int:category_id>/', edit_category, name='edit_category'),
    path('categories/delete_category/<int:category_id>/', delete_category, name='delete_category'),

]