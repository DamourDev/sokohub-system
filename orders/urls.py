from django.urls import path
from . import views

urlpatterns = [
    path('my-orders/', views.customer_orders, name='customer_orders'),
    path('vendor-orders/', views.vendor_orders, name='vendor_orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirm/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]