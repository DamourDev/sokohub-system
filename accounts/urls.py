from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-mfa/', views.verify_mfa, name='verify_mfa'),
    path('settings/profile/', views.edit_profile, name='edit_profile'),
    # path('settings/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('settings/mfa/enable/email/', views.enable_email_mfa, name='enable_email_mfa'),
    path('settings/mfa/verify/email/', views.enable_email_mfa, name='enable_email_mfa'),
    path('settings/mfa/verify/email/setup/', views.verify_email_setup, name='verify_email_setup'),
    path('settings/mfa-settings/', views.mfa_settings, name='mfa_settings'),
    path('settings/mfa/enable/app/', views.enable_app_mfa, name='enable_app_mfa'),
    path('settings/mfa/disable/', views.disable_mfa, name='disable_mfa'),


    path('settings/password/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/change_password.html',
             success_url='/accounts/settings/profile/'
         ),
         name='change_password'),

    path('reset-password/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
            
         ),
         name='reset_password'),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             
         ),
         name='password_reset_confirm'),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),

]