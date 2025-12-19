from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import EmailOTP 

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user

        # MFA CHECK
        if getattr(user, 'mfa_enabled', False):
            if user.mfa_method == 'email':
                otp, created = EmailOTP.objects.get_or_create(user=user)
                otp.generate_code()
                if user.email:
                    try:
                        send_mail(
                            'SokoHub Verification Code',
                            f'Your code is: {otp.otp_code}',
                            settings.EMAIL_HOST_USER,
                            [user.email],
                            fail_silently=False
                        )
                        messages.info(request, "Code sent to your email.")
                    except Exception as e:
                        messages.error(request, "Email failed to send.")
                return resolve_url('verify_mfa')

            elif user.mfa_method == 'app':
                return resolve_url('verify_mfa')

        # REDIRECT LOGIC
        if user.is_superuser or user.is_staff:
            return resolve_url('/admin/')
        elif user.user_type == 'vendor':
            return resolve_url('vendor_dashboard') 
        else:
            return resolve_url('products_list')
        

    def get_signup_redirect_url(self, request):
        user = request.user
        if user.user_type == 'vendor':
            return resolve_url('vendor_dashboard')
        return resolve_url('products_list')


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        selected_type = request.POST.get('user_type')
        if selected_type in ['vendor', 'customer']:
            user.user_type = selected_type
            user.save()
        return user

    # This handles the redirect after a NEW signup
    def get_signup_redirect_url(self, request):
        selected_type = request.POST.get('user_type')
        if selected_type == 'vendor':
            return resolve_url('vendor_dashboard')
        return resolve_url('products_list')

    # This handles the redirect if they login again later via Google
    def get_connect_redirect_url(self, request, socialaccount):
        if request.user.user_type == 'vendor':
            return resolve_url('vendor_dashboard')
        return resolve_url('products_list')