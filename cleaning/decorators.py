"""
Permission decorators for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import UserProfile


def require_customer(view_func):
    """
    Decorator to ensure user is logged in and is a customer
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'customer':
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Only customers can access this page")
        except UserProfile.DoesNotExist:
            return HttpResponseForbidden("User profile not found")
    return wrapper


def require_provider(view_func):
    """
    Decorator to ensure user is logged in and is a verified provider
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'provider' and user_profile.is_verified_by_admin:
                return view_func(request, *args, **kwargs)
            elif user_profile.user_type == 'provider' and not user_profile.is_verified_by_admin:
                return HttpResponseForbidden("Your account is pending admin verification")
            else:
                return HttpResponseForbidden("Only verified service providers can access this page")
        except UserProfile.DoesNotExist:
            return HttpResponseForbidden("User profile not found")
    return wrapper


def require_admin(view_func):
    """
    Decorator to ensure user is logged in and is an admin user
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Only administrators can access this page")
    return wrapper
