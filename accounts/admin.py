from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmailOTP

class CustomUserAdmin(UserAdmin):
    list_display = ('id','username', 'email', 'user_type', 'phone', 'location', 'mfa_enabled', 'mfa_method')
    list_filter = ('user_type',)
    search_fields = ('username', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('MFA Settings', {'fields': ('mfa_enabled', 'mfa_method')}),    
    )
    
admin.site.register(CustomUser, CustomUserAdmin) 

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'created_at', 'expires_at')
    search_fields = ('user__username', 'otp_code')
    list_filter = ('created_at', 'expires_at')
    readonly_fields = ( 'created_at', 'expires_at')