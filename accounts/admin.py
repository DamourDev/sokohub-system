from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('id','username', 'email', 'user_type', 'phone', 'location')
    list_filter = ('user_type',)
    search_fields = ('username', 'email')
    
admin.site.register(CustomUser, CustomUserAdmin) 
