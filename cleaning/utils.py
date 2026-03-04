"""
Utility functions for the cleaning app
"""
from django.contrib.auth.models import User
from .models import Notification, Review


def create_notification(user, notification_type, message, booking=None):
    """
    Create a notification for a user
    
    Args:
        user: User object who receives notification
        notification_type: Type of notification (booking_request, status_update, etc.)
        message: Notification message text
        booking: Optional Booking object related to notification
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        booking=booking
    )
    return notification


def notify_provider_booking_request(booking):
    """
    Notify provider about new booking request
    
    Args:
        booking: Booking object
    """
    if booking.provider:
        message = f"New booking request for {booking.service.name} on {booking.date_time.strftime('%Y-%m-%d %H:%M')}"
        create_notification(
            user=booking.provider,
            notification_type='booking_request',
            message=message,
            booking=booking
        )


def notify_customer_booking_status(booking):
    """
    Notify customer about booking status change
    
    Args:
        booking: Booking object
    """
    message = f"Your booking for {booking.service.name} is now {booking.get_status_display()}"
    create_notification(
        user=booking.customer,
        notification_type='status_update',
        message=message,
        booking=booking
    )


def notify_provider_verification_update(user, status):
    """
    Notify provider about verification status
    
    Args:
        user: User object (provider)
        status: 'verified' or 'rejected'
    """
    if status == 'verified':
        message = "Congratulations! Your account has been verified by admin. You can now accept bookings."
    else:
        message = "Your account verification has been rejected. Please contact admin for more details."
    
    create_notification(
        user=user,
        notification_type='provider_update',
        message=message
    )


def update_provider_rating(provider):
    """
    Update provider's rating based on all reviews
    
    Args:
        provider: User object (provider)
    """
    from .models import UserProfile
    
    reviews = Review.objects.filter(booking__provider=provider)
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
        try:
            profile = UserProfile.objects.get(user=provider)
            profile.rating = round(avg_rating, 1)
            profile.save()
        except UserProfile.DoesNotExist:
            pass


def update_service_rating(service):
    """
    Update service's average rating based on all reviews
    
    Args:
        service: Service object
    """
    reviews = Review.objects.filter(booking__service=service)
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
        service.average_rating = round(avg_rating, 1)
        service.save()


def get_pending_bookings(user):
    """
    Get all pending bookings for a user
    
    Args:
        user: User object
        
    Returns:
        QuerySet of pending Booking objects
    """
    from .models import UserProfile, Booking
    
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.user_type == 'customer':
            return Booking.objects.filter(customer=user, status='pending').order_by('-created_at')
        elif profile.user_type == 'provider':
            return Booking.objects.filter(provider=user, status='pending').order_by('-created_at')
    except UserProfile.DoesNotExist:
        pass
    
    return Booking.objects.none()


def get_active_bookings(user):
    """
    Get all active (in-progress) bookings for a user
    
    Args:
        user: User object
        
    Returns:
        QuerySet of active Booking objects
    """
    from .models import UserProfile, Booking
    
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.user_type == 'customer':
            return Booking.objects.filter(
                customer=user,
                status__in=['confirmed', 'in_progress', 'work_started']
            ).order_by('-date_time')
        elif profile.user_type == 'provider':
            return Booking.objects.filter(
                provider=user,
                status__in=['confirmed', 'in_progress', 'work_started']
            ).order_by('-date_time')
    except UserProfile.DoesNotExist:
        pass
    
    return Booking.objects.none()


def get_completed_bookings(user):
    """
    Get all completed bookings for a user
    
    Args:
        user: User object
        
    Returns:
        QuerySet of completed Booking objects
    """
    from .models import UserProfile, Booking
    
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.user_type == 'customer':
            return Booking.objects.filter(customer=user, status='completed').order_by('-date_time')
        elif profile.user_type == 'provider':
            return Booking.objects.filter(provider=user, status='completed').order_by('-date_time')
    except UserProfile.DoesNotExist:
        pass
    
    return Booking.objects.none()
