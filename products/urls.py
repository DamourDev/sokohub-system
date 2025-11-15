from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
]
