from django.db import models
from accounts.models import CustomUser 

class Category(models.Model):
    # Self-referential foreign key for hierarchical categories
    parent = models.ForeignKey(
        'self', 
        related_name='children', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
    #     return self.name
    # def get_hierarchy(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' > '.join(full_path[::-1])

    # Fixes "Categorys" typo in admin panel
    class Meta:
        verbose_name_plural = 'categories'

class Product(models.Model):
    PRODUCT_STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    vendor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='products' 
    )
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    status = models.CharField(
        max_length=10, 
        choices=PRODUCT_STATUS_CHOICES, 
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products',
               
    )
    unit = models.CharField(max_length=20, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.name} by {self.vendor.username}"
    

class VariationManager(models.Manager):
    def colorrs(self):
        return super(VariationManager, self).get_queryset().filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).get_queryset().filter(variation_category='size', is_active=True)
    def capacities(self):
        return super(VariationManager, self).get_queryset().filter(variation_category='capacity', is_active=True)
    def materials(self):
        return super(VariationManager, self).get_queryset().filter(variation_category='material', is_active=True)
    
VARIATION_CATEGORIES = (
    ('color', 'Color'),
    ('size', 'Size'),
    ('capacity', 'Capacity'),
    ('material', 'Material'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORIES)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='product_gallery/', blank=True, null=True)

    def __str__(self):
        return self.product.name
    
    class Meta:
        verbose_name_plural = 'Product Gallery'