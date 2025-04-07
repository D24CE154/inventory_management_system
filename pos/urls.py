from django.urls import path, include
# pos/urls.py
from .views import salesExecutiveDashboard, create_sale, razorpay_callback, product_search

urlpatterns = [
    path("salesExecutiveDashboard/", salesExecutiveDashboard, name="salesExecutiveDashboard"),
    path('create-sale/', create_sale, name='create_sale'),
    path('payment/callback/', razorpay_callback, name='razorpay_callback'),
    path('product-search/', product_search, name='product_search'),
]