from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class ServiceCategory(models.Model):
    """Service category for organizing cleaning services"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['name']
        
    def __str__(self):
        return self.name

class Service(models.Model):
    SERVICE_TYPES = [
        ('deep', 'Deep Cleaning'),
        ('sofa', 'Sofa Cleaning'),
        ('movein', 'Move-In Service'),
    ]
    
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)
    is_best_value = models.BooleanField(default=False)
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('provider', 'Provider'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    completed_jobs = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='verified')
    verification_document = models.FileField(upload_to='provider_docs/', blank=True, null=True, help_text='Identity proof for service providers')
    is_verified_by_admin = models.BooleanField(default=False, help_text='Admin approval flag for providers')
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('work_started', 'Work Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_bookings')
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='provider_bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    notes = models.TextField(blank=True)
    completion_notes = models.TextField(blank=True, help_text='Provider notes on job completion')
    photo = models.ImageField(upload_to='booking_photos/', blank=True, null=True)
    rating_submitted = models.BooleanField(default=False)
    booking_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Auto-set booking expiry to 24 hours from creation if pending
        if self.pk is None and self.status == 'pending':
            self.booking_expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.service.name} - {self.customer.username} - {self.status}"

class Review(models.Model):
    """Customer review and rating for completed services"""
    RATING_CHOICES = [(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        # Update service and provider rating when review is created
        super().save(*args, **kwargs)
        self._update_ratings()
    
    def _update_ratings(self):
        """Update provider and service average ratings"""
        booking = self.booking
        service = booking.service
        provider = booking.provider
        
        if provider:
            reviews = Review.objects.filter(booking__provider=provider)
            if reviews.exists():
                avg_rating = sum(r.rating for r in reviews) / reviews.count()
                provider_profile = UserProfile.objects.get(user=provider)
                provider_profile.rating = round(avg_rating, 1)
                provider_profile.save()
        
        if service:
            reviews = Review.objects.filter(booking__service=service)
            if reviews.exists():
                avg_rating = sum(r.rating for r in reviews) / reviews.count()
                service.average_rating = round(avg_rating, 1)
                service.save()
    
    def __str__(self):
        return f"Review for {self.booking.service.name} - {self.rating}★"

class Payment(models.Model):
    """Payment records for bookings"""
    PAYMENT_GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('razorpay', 'Razorpay'),
        ('paypal', 'PayPal'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_gateway = models.CharField(max_length=20, choices=PAYMENT_GATEWAY_CHOICES, default='stripe')
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"Payment for {self.booking.service.name} - {self.status}"

class Notification(models.Model):
    """System notifications for users about bookings and status updates"""
    NOTIFICATION_TYPES = [
        ('booking_request', 'Booking Request'),
        ('status_update', 'Status Update'),
        ('review_posted', 'Review Posted'),
        ('provider_update', 'Provider Verification Update'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username} - {self.notification_type}"
