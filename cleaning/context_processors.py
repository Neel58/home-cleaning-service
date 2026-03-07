"""
Context processors for the cleaning app
Adds commonly used variables to all templates
"""
from .models import UserProfile, Notification


def user_profile_context(request):
    """
    Add user profile information to all templates
    Ensures user.userprofile is available in templates without additional queries
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            context['user_profile'] = profile
            # Also add to request.user for template access
            request.user.userprofile = profile
        except UserProfile.DoesNotExist:
            context['user_profile'] = None
    
    return context


def notifications_context(request):
    """
    Add unread notifications count to all templates for authenticated users
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            unread_count = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
            context['unread_notifications_count'] = unread_count
        except Exception:
            context['unread_notifications_count'] = 0
    
    return context
