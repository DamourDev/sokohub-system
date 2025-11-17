from django.urls import path
from . import views

urlpatterns = [
    path('my-orders/', views.customer_orders, name='customer_orders'),
    path('vendor-orders/', views.vendor_orders, name='vendor_orders'),
    path('checkout/<int:pk>/', views.checkout, name='checkout'),
    path('order-confirm/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]