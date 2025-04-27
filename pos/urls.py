from django.urls import path
from .views import (
    salesExecutiveDashboard,
    add_customer,
    create_sale,
    fetch_products_by_category,
    generate_invoice,
    fetch_product_by_imei,
    check_stock,
    sales_history,
    customer_list
)

urlpatterns = [
    path("salesExecutiveDashboard/", salesExecutiveDashboard, name="salesExecutiveDashboard"),
    path("add_customer/", add_customer, name="add_customer"),
    path("create_sale/", create_sale, name="create_sale"),
    path("fetch_products_by_category/<int:category_id>/", fetch_products_by_category, name="fetch_products_by_category"),
    path("fetch_product_by_imei/", fetch_product_by_imei, name="fetch_product_by_imei"),
    path("invoice/<int:sale_id>/", generate_invoice, name="generate_invoice"),
    path("api/check-stock/", check_stock, name="check_stock"),
    path("sales_history/", sales_history, name="sales_history"),
    path("customer_list",customer_list,name="customer_list"),
]