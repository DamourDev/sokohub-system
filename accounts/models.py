from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
import random

class CustomUser(AbstractUser):
   
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )
   
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='customer',
        verbose_name='User Type' 
    )
    phone = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    mfa_enabled = models.BooleanField(default=False)

    MFA_CHOICES = (
        ('email', 'Email OTP'),
        ('app', 'Authenticator App'),
    )

    mfa_method = models.CharField(
        max_length=10, 
        choices=MFA_CHOICES, 
        default='email',
        verbose_name='MFA Method' 
    )
   
    def __str__(self):
        return f"{self.username} is ({self.user_type})"

class EmailOTP(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='email_otp'
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def generate_code(self):
        self.otp_code = f"{random.randint(100000, 999999)}" 
        self.created_at = timezone.now()
        self.expires_at = self.created_at + timedelta(minutes=5)
        self.save()
    def is_valid(self):
        return timezone.now() < self.expires_at
    
    def __str__(self): 
        return f"OTP for {self.user.username} is {self.otp_code}"