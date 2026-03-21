"""
Permission decorators for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile


def require_customer(view_func):
    """
    Decorator to ensure user is logged in and is a customer.
    Gracefully redirects unauthorized access with a flash message.
    """
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'customer':
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Only customers can access this page. You are logged in as a provider.')
                return redirect('logged_in_home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found. Please contact support.')
            return redirect('logged_in_home')
    return wrapper


def require_provider(view_func):
    """
    Decorator to ensure user is logged in and is a verified provider.
    Gracefully redirects unauthorized access with a flash message.
    """
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'provider' and user_profile.is_verified_by_admin:
                return view_func(request, *args, **kwargs)
            elif user_profile.user_type == 'provider' and not user_profile.is_verified_by_admin:
                messages.error(request, 'Your account is pending admin verification. You will be able to access this once approved.')
                return redirect('logged_in_home')
            else:
                messages.error(request, 'Only verified service providers can access this page. You are logged in as a customer.')
                return redirect('logged_in_home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found. Please contact support.')
            return redirect('logged_in_home')
    return wrapper


def require_admin(view_func):
    """
    Decorator to ensure user is logged in and is an admin user.
    Gracefully redirects unauthorized access with a flash message.
    """
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Only administrators can access this page.')
            return redirect('logged_in_home')
    return wrapper
