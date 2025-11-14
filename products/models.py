from django.db import models
from accounts.models import CustomUser 

class Product(models.Model):
    PRODUCT_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    vendor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'vendor'}, 
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    status = models.CharField(
        max_length=10, 
        choices=PRODUCT_STATUS_CHOICES, 
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.vendor.username}"