from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-mfa/', views.verify_mfa, name='verify_mfa'),
    path('settings/profile/', views.edit_profile, name='edit_profile'),
    path('settings/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('settings/mfa/enable/email/', views.enable_email_mfa, name='enable_email_mfa'),
    path('settings/mfa/verify/email/', views.enable_email_mfa, name='enable_email_mfa'),
    path('settings/mfa-settings/', views.mfa_settings, name='mfa_settings'),

]