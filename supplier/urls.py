from django.urls import path
from . import views

urlpatterns = [
    path("suppliers/", views.supplierDashboard, name="suppliers"),
    path("add-supplier/", views.add_supplier, name="add_supplier"),
    path("edit-supplier/<str:supplier_id>/", views.edit_supplier, name="edit_supplier"),
    path("delete-supplier/<str:supplier_id>/", views.delete_supplier, name="delete_supplier"),
    path("view-supplier/<str:supplier_id>/", views.view_supplier, name="view_supplier"),
    path("search-supplier/", views.search_supplier, name="search_supplier"),

    path("purchase-orders/", views.purchase_order_list, name="purchase_order_list"),
    path("add-purchase-order/", views.add_purchase_order, name="add_purchase_order"),
    path("edit-purchase-order/<int:order_id>/", views.edit_purchase_order, name="edit_purchase_order"),
    path("delete-purchase-order/<int:order_id>/", views.delete_purchase_order, name="delete_purchase_order"),

    path("purchase-order-items/", views.purchase_order_item_list, name="purchase_order_item_list"),
    path("add-purchase-order-item/", views.add_purchase_order_item, name="add_purchase_order_item"),
    path("edit-purchase-order-item/<int:item_id>/", views.edit_purchase_order_item, name="edit_purchase_order_item"),
    path("delete-purchase-order-item/<int:item_id>/", views.delete_purchase_order_item, name="delete_purchase_order_item"),
]