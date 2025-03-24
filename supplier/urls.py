from django.urls import path
from .views import (
    supplierDashboard, add_supplier, edit_supplier,
    delete_supplier, search_supplier, view_supplier
)

urlpatterns = [
    path("suppliers/", supplierDashboard, name="suppliers"),
    path("add-supplier/", add_supplier, name="add_supplier"),
    path("edit-supplier/<str:supplier_id>/", edit_supplier, name="edit_supplier"),
    path("delete-supplier/<str:supplier_id>/", delete_supplier, name="delete_supplier"),
    path("view-supplier/<str:supplier_id>/", view_supplier, name="view_supplier"),
    path("search-supplier/", search_supplier, name="search_supplier"),
]