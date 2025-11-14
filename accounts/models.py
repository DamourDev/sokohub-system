from django.db import models
from django.contrib.auth.models import AbstractUser

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
    phone = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

   
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"