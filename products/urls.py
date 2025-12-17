from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('products/', views.products_list, name='products_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('vendor-products/', views.vendor_products_list, name='vendor_products_list'),
    path('vendor/<int:vendor_id>/products/', views.vendor_public_products, name='vendor_public_products'),
    path('related-products/<int:pk>/', views.related_products_list, name='related_products_list'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/decrement/', views.cart_decrement, name='cart_decrement'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('search/', views.product_search, name='product_search'),  
    path('search-suggestions/', views.product_search_suggestions, name='product_search_suggestions'),
]
