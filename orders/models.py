from django.db import models 
from accounts.models import CustomUser
from products.models import Product

class Order(models.Model): 
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('shipped', 'Shipped'),
    )

    parent =  models.ForeignKey(
        'self', 
        related_name='sub_orders',    
        on_delete=models.CASCADE, 
        blank=True,
        null=True
    )

    vendor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendor_orders' 
    )
    
    
    customer = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='orders'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=25, 
        choices=ORDER_STATUS_CHOICES, 
        default='pending'
    )
    delivery_address = models.CharField(max_length=500)
    phone = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.parent:
            return f"Sub-Order #{self.id} for {self.vendor} (Parent #{self.parent.id})"
        return f"Main Order #{self.id} by {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT 
    )
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"