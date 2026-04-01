from django.db import models
from django.contrib.auth.models import User

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=[('admin', 'Admin'), ('vendor', 'Vendor'), ('customer', 'Customer')],
        default='customer'
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, help_text='Profile avatar image')
    
    class Meta:
        db_table = 'api_profile'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product') # One review per user per product
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.rating}⭐)"

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    file_url = models.URLField(blank=True, null=True)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, null=True, blank=True)
    review_count = models.IntegerField(default=0)
    class Meta:
        db_table = 'api_product'
    def update_rating_stats(self):
        """Recalculate average rating and count"""
        stats = self.reviews.aggregate(avg=models.Avg('rating'), count=models.Count('id'))
        self.average_rating = stats['avg'] or 0.00
        self.review_count = stats['count'] or 0
        self.save()
    def __str__(self):
        return self.title


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_order'
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    license_key = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'api_orderitem'
    
    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    

    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    class Meta:
        db_table = 'api_cart'
    
    def __str__(self):
        return f"Cart for {self.user.username}"
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
  
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) 
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

    def is_valid(self):
        """Check if coupon is active and not expired"""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True