from django.contrib import admin
from .models import Product

# @admin.register(Product) 
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'stock')
    list_filter = ('status', 'vendor')
    search_fields = ('name', 'vendor__username')
   
admin.site.register(Product, ProductAdmin)