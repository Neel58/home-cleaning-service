from django.contrib import admin
from .models import Service, UserProfile, Booking, Review, ServiceCategory, Notification, Payment

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'category', 'price', 'duration', 'average_rating', 'is_best_value')
    list_filter = ('service_type', 'is_best_value', 'category')
    search_fields = ('name', 'description')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone', 'city', 'rating', 'completed_jobs', 'verification_status', 'is_verified_by_admin')
    list_filter = ('user_type', 'verification_status', 'is_verified_by_admin')
    search_fields = ('user__username', 'user__email', 'phone', 'city')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'provider', 'service', 'date_time', 'status', 'payment_status', 'rating_submitted', 'created_at')
    list_filter = ('status', 'payment_status', 'service', 'created_at', 'rating_submitted')
    search_fields = ('customer__username', 'provider__username', 'location')
    date_hierarchy = 'created_at'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('booking__service__name', 'booking__customer__username')
    readonly_fields = ('created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'payment_gateway', 'status', 'paid_at', 'created_at')
    list_filter = ('payment_gateway', 'status', 'created_at')
    search_fields = ('booking__id', 'transaction_id', 'booking__customer__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
