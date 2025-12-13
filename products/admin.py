from django.contrib import admin
from .models import Product, Category, Variation

# @admin.register(Product) 
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'stock')
    list_filter = ('status', 'vendor')
    search_fields = ('name', 'vendor__username')
   
admin.site.register(Product, ProductAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_filter = ('variation_category', 'is_active')
    search_fields = ('product__name', 'variation_value')
    list_editable = ('is_active',)