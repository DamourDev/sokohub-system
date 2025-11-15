from django.urls import path
from . import views

urlpatterns = [
    path('my-orders/', views.customer_orders, name='customer_orders'),
]