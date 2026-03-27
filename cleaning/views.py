from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden

from .models import Service, UserProfile, Booking, Review, ServiceCategory, Notification, Payment
from .forms import (
    ReviewForm, BookingForm, JobUpdateForm, BookingCancelForm,
    ServiceCategoryForm, ProviderVerificationForm, UserProfileUpdateForm,
    ServiceFilterForm
)
from .decorators import require_customer, require_provider, require_admin
from .utils import (
    create_notification, notify_provider_booking_request,
    notify_customer_booking_status, notify_provider_verification_update,
    update_provider_rating, update_service_rating,
    get_pending_bookings, get_active_bookings, get_completed_bookings
)

# ======================== AUTHENTICATION VIEWS ========================

def signup_view(request):
    """Handle user registration for both customers and providers"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        user_type = request.POST.get('user_type')
        phone = request.POST.get('phone')
        name = request.POST.get('name', email)
        
        # Validation
        if not all([email, password, password_confirm, user_type, phone]):
            messages.error(request, 'All fields are required')
            return render(request, 'cleaning/signup.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'cleaning/signup.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'cleaning/signup.html')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'cleaning/signup.html')
        
        try:
            # Create user with email as username
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                is_active=True  # Explicitly set to active on creation
            )
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone=phone
            )
            
            # Set verification status based on type
            if user_type == 'provider':
                profile.verification_status = 'pending'
                profile.save()
                messages.success(request, 'Account created! Your account is pending admin verification.')
            else:
                messages.success(request, 'Account created successfully! Please log in.')
            
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'cleaning/signup.html')
    
    return render(request, 'cleaning/signup.html')


def login_view(request):
    """Handle user login for customers, providers, and admins"""
    # If user is already authenticated, redirect to their appropriate dashboard
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.user_type == 'customer':
                return redirect('logged_in_home')
            elif profile.user_type == 'provider':
                if profile.is_verified_by_admin:
                    return redirect('logged_in_home')
                else:
                    messages.warning(request, 'Your account is pending admin verification.')
                    return redirect('logout')
            elif request.user.is_staff and request.user.is_superuser:
                return redirect('admin:index')
        except UserProfile.DoesNotExist:
            return redirect('logout')
        return redirect('logged_in_home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        # First, check if user exists in database
        try:
            user_obj = User.objects.get(username=email)
            if not user_obj.is_active:
                messages.error(request, 'Your account has been disabled. Please contact support.')
                return render(request, 'cleaning/login.html')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'cleaning/login.html')
        
        # Now try to authenticate
        user = authenticate(request, username=email, password=password)
        if user is not None:
            try:
                profile = UserProfile.objects.get(user=user)
                
                if user_type == 'customer' and profile.user_type == 'customer':
                    login(request, user)
                    return redirect('logged_in_home')
                elif user_type == 'provider' and profile.user_type == 'provider':
                    if profile.is_verified_by_admin:
                        login(request, user)
                        return redirect('logged_in_home')
                    else:
                        messages.warning(request, 'Your account is pending admin verification. You cannot log in yet.')
                        return render(request, 'cleaning/login.html')
                else:
                    messages.error(request, 'Invalid user type for this account')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact support.')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'cleaning/login.html')


def logout_view(request):
    """Handle user logout"""
    user_email = request.user.email if request.user.is_authenticated else None
    logout(request)
    messages.success(request, f'You have been logged out successfully. See you again soon!')
    return redirect('login')


# ======================== CUSTOMER VIEWS ========================

@login_required
def index(request):
    """Customer homepage with featured services"""
    featured_services = Service.objects.filter(is_best_value=True)[:6]
    total_customers = User.objects.count()
    total_bookings = Booking.objects.filter(status='completed').count()
    
    context = {
        'featured_services': featured_services,
        'total_customers': total_customers,
        'total_bookings': total_bookings,
    }
    return render(request, 'cleaning/index.html', context)


@login_required
def logged_in_home(request):
    """Logged-in user homepage with personalized content"""
    # Redirect admin users to admin dashboard
    if request.user.is_staff and request.user.is_superuser:
        return redirect('admin:index')
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        user_type = profile.user_type
    except UserProfile.DoesNotExist:
        return redirect('logout')
    
    if user_type == 'customer':
        # For customers, get their active and pending bookings
        active_bookings = get_active_bookings(request.user)
        pending_bookings = get_pending_bookings(request.user)
        featured_services = Service.objects.filter(is_best_value=True)[:6]
        recent_reviews = Review.objects.filter(booking__customer=request.user).order_by('-created_at')[:3]
        
        # Get unread notifications
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
        
        context = {
            'user_type': user_type,
            'profile': profile,
            'active_bookings': active_bookings,
            'pending_bookings': pending_bookings,
            'featured_services': featured_services,
            'recent_reviews': recent_reviews,
            'notifications': notifications,
        }
    elif user_type == 'provider':
        # For providers, get their active jobs and earnings
        active_jobs = Booking.objects.filter(
            provider=request.user,
            status__in=['confirmed', 'in_progress', 'work_started']
        ).order_by('-date_time')
        
        completed_jobs = Booking.objects.filter(
            provider=request.user,
            status='completed'
        ).order_by('-date_time')[:5]
        
        # Calculate total earnings
        try:
            total_earnings = Payment.objects.filter(
                booking__provider=request.user,
                status='paid'
            ).aggregate(total=Sum('amount'))['total'] or 0
        except:
            total_earnings = 0
        
        # Get average rating
        reviews = Review.objects.filter(booking__provider=request.user)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Get unread notifications
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
        
        context = {
            'user_type': user_type,
            'profile': profile,
            'active_jobs': active_jobs,
            'completed_jobs': completed_jobs,
            'total_earnings': total_earnings,
            'avg_rating': round(avg_rating, 1),
            'notifications': notifications,
        }
    else:
        # Admin users
        return redirect('admin:index')
    
    return render(request, 'cleaning/logged_in_home.html', context)


@require_customer
def customer_dashboard(request):
    """Customer dashboard showing bookings and activity"""
    pending_bookings = get_pending_bookings(request.user)
    active_bookings = get_active_bookings(request.user)
    completed_bookings = get_completed_bookings(request.user)
    
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    
    # Get unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'pending_bookings': pending_bookings,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'profile': profile,
        'notifications': notifications,
    }
    return render(request, 'cleaning/customer/dashboard.html', context)


@login_required
def services(request):
    """Service listing with filtering and search"""
    # Redirect providers to their dashboard instead
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.user_type == 'provider':
            messages.info(request, 'Service providers cannot browse customer services.')
            return redirect('provider_dashboard')
    except UserProfile.DoesNotExist:
        pass
    
    services_list = Service.objects.filter(category__is_active=True)
    form = ServiceFilterForm(request.GET)
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by')
        
        if search:
            services_list = services_list.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        if category:
            services_list = services_list.filter(category=category)
        
        if min_price:
            services_list = services_list.filter(price__gte=min_price)
        
        if max_price:
            services_list = services_list.filter(price__lte=max_price)
        
        # Apply sorting
        if sort_by == 'price_asc':
            services_list = services_list.order_by('price')
        elif sort_by == 'price_desc':
            services_list = services_list.order_by('-price')
        elif sort_by == 'rating_desc':
            services_list = services_list.order_by('-average_rating')
    
    context = {
        'services': services_list,
        'form': form,
    }
    return render(request, 'cleaning/services.html', context)


@login_required
def service_detail(request, service_id):
    """Service detail view with booking form"""
    service = get_object_or_404(Service, id=service_id)
    reviews = Review.objects.filter(booking__service=service).order_by('-created_at')[:5]
    
    # Prevent service providers from booking services
    is_provider = False
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.user_type == 'provider':
            is_provider = True
    except UserProfile.DoesNotExist:
        pass
    
    # Get user's booking status for this service (if logged in)
    user_booking = None
    if request.user.is_authenticated:
        # Get the most recent booking for this service by this user
        user_booking = Booking.objects.filter(
            customer=request.user,
            service=service
        ).exclude(status='cancelled').order_by('-created_at').first()
    
    if request.method == 'POST':
        # Check if user is a provider - if yes, prevent booking
        if is_provider:
            messages.error(request, 'Service providers cannot book services.')
            form = BookingForm()
        else:
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.customer = request.user
                booking.service = service
                booking.status = 'pending'
                booking.save()
                
                messages.success(request, 'Booking created! Waiting for provider response.')
                create_notification(
                    user=request.user,
                    notification_type='booking_request',
                    message=f'Your booking for {service.name} has been created.',
                    booking=booking
                )
                return redirect('customer_dashboard')
    else:
        form = BookingForm()
    
    context = {
        'service': service,
        'form': form,
        'reviews': reviews,
        'user_booking': user_booking,
        'is_provider': is_provider,
    }
    return render(request, 'cleaning/service_detail.html', context)


@login_required
def booking_cancel(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if booking.status in ['completed', 'cancelled']:
        messages.error(request, 'This booking cannot be cancelled')
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        form = BookingCancelForm(request.POST)
        if form.is_valid():
            booking.status = 'cancelled'
            booking.save()
            
            messages.success(request, 'Booking cancelled successfully')
            create_notification(
                user=request.user,
                notification_type='status_update',
                message='Your booking has been cancelled.',
                booking=booking
            )
            
            if booking.provider:
                create_notification(
                    user=booking.provider,
                    notification_type='status_update',
                    message=f'Booking for {booking.service.name} has been cancelled.',
                    booking=booking
                )
            
            return redirect('customer_dashboard')
    else:
        form = BookingCancelForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'cleaning/booking_cancel.html', context)


@require_customer
def submit_review(request, booking_id):
    """Submit a review for a completed booking"""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if booking.status != 'completed':
        messages.error(request, 'You can only review completed bookings')
        return redirect('customer_dashboard')
    
    if hasattr(booking, 'review') and booking.review:
        messages.info(request, 'You have already reviewed this booking')
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            
            booking.rating_submitted = True
            booking.save()
            
            # Update ratings
            update_provider_rating(booking.provider)
            update_service_rating(booking.service)
            
            messages.success(request, 'Review submitted successfully!')
            
            # Notify provider
            if booking.provider:
                create_notification(
                    user=booking.provider,
                    notification_type='review_posted',
                    message=f'You received a {review.rating}★ review for {booking.service.name}',
                    booking=booking
                )
            
            return redirect('customer_dashboard')
    else:
        form = ReviewForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'cleaning/review_form.html', context)


@require_customer
def user_profile(request):
    """User profile view with booking history"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
        context = {
            'bookings': bookings,
            'profile': profile,
        }
        return render(request, 'cleaning/user_profile.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found. Please contact support.')
        return redirect('logged_in_home')


# ======================== PROVIDER VIEWS ========================

@require_provider
def provider_dashboard(request):
    """Provider dashboard showing pending and active jobs"""
    # Get unverified pending bookings (ones not yet accepted)
    new_requests = Booking.objects.filter(
        status='pending',
        provider__isnull=True
    ).order_by('-created_at')
    
    # Get bookings assigned to this provider
    active_jobs = Booking.objects.filter(
        provider=request.user,
        status__in=['confirmed', 'in_progress', 'work_started']
    ).order_by('-date_time')
    
    completed_jobs = Booking.objects.filter(
        provider=request.user,
        status='completed'
    ).order_by('-date_time')[:10]
    
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    
    # Calculate total earnings
    try:
        total_earnings = Payment.objects.filter(
            booking__provider=request.user,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
    except:
        total_earnings = 0
    
    # Get average rating
    reviews = Review.objects.filter(booking__provider=request.user)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()
    
    # Get total completed jobs count
    total_completed = Booking.objects.filter(
        provider=request.user,
        status='completed'
    ).count()
    
    # Get unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'new_requests': new_requests,
        'active_jobs': active_jobs,
        'completed_jobs': completed_jobs,
        'profile': profile,
        'total_earnings': total_earnings,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
        'total_completed': total_completed,
        'active_job_count': active_jobs.count(),
        'new_request_count': new_requests.count(),
        'notifications': notifications,
    }
    return render(request, 'cleaning/provider_dashboard.html', context)


@require_provider
def booking_accept(request, booking_id):
    """Accept a booking request"""
    booking = get_object_or_404(Booking, id=booking_id, status='pending')
    
    # Check if already assigned
    if booking.provider:
        messages.error(request, 'This booking has already been accepted')
        return redirect('provider_dashboard')
    
    booking.provider = request.user
    booking.status = 'confirmed'
    booking.save()
    
    messages.success(request, 'Job accepted!')
    
    # Notify customer
    create_notification(
        user=booking.customer,
        notification_type='status_update',
        message=f'Your booking for {booking.service.name} has been accepted by a provider!',
        booking=booking
    )
    
    return redirect('provider_dashboard')


@require_provider
def booking_reject(request, booking_id):
    """Reject a booking request"""
    booking = get_object_or_404(Booking, id=booking_id, status='pending')
    
    if booking.provider and booking.provider != request.user:
        return HttpResponseForbidden("You don't have permission to reject this booking")
    
    booking.status = 'cancelled'
    booking.provider = None
    booking.save()
    
    messages.success(request, 'Booking rejected')
    
    # Notify customer if it was confirmed before
    if booking.provider:
        create_notification(
            user=booking.customer,
            notification_type='status_update',
            message=f'Your booking for {booking.service.name} was rejected by the provider.',
            booking=booking
        )
    
    return redirect('provider_dashboard')


@require_provider
def provider_update_job(request, booking_id):
    """Update job status and add work proof"""
    booking = get_object_or_404(Booking, id=booking_id, provider=request.user)
    
    if request.method == 'POST':
        form = JobUpdateForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            booking = form.save()
            
            messages.success(request, 'Job status updated!')
            
            # Notify customer about status change
            notify_customer_booking_status(booking)
            
            return redirect('provider_dashboard')
    else:
        form = JobUpdateForm(instance=booking)
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'cleaning/provider_update.html', context)


@login_required
def provider_profile(request):
    """Provider profile view with ratings and booking history"""
    # Allow both self-viewing and public viewing
    provider_id = request.GET.get('id')
    
    if provider_id:
        try:
            provider = User.objects.get(id=provider_id)
            profile = UserProfile.objects.get(user=provider)
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'Provider not found')
            return redirect('services')
    else:
        profile = get_object_or_404(UserProfile, user=request.user)
        provider = request.user
    
    if profile.user_type != 'provider':
        return redirect('services')
    
    reviews = Review.objects.filter(booking__provider=provider).order_by('-created_at')
    completed_jobs = Booking.objects.filter(provider=provider, status='completed').count()
    
    context = {
        'profile': profile,
        'provider': provider,
        'reviews': reviews,
        'completed_jobs': completed_jobs,
    }
    return render(request, 'cleaning/provider_profile.html', context)


# ======================== ADMIN VIEWS ========================

@require_admin
def provider_verification_list(request):
    """Admin view to list and verify providers"""
    pending_providers = UserProfile.objects.filter(
        user_type='provider',
        verification_status='pending',
        is_verified_by_admin=False
    ).select_related('user')
    
    verified_providers = UserProfile.objects.filter(
        user_type='provider',
        is_verified_by_admin=True
    ).select_related('user')
    
    rejected_providers = UserProfile.objects.filter(
        user_type='provider',
        verification_status='rejected'
    ).select_related('user')
    
    context = {
        'pending_providers': pending_providers,
        'verified_providers': verified_providers,
        'rejected_providers': rejected_providers,
    }
    return render(request, 'cleaning/admin/provider_list.html', context)


@require_admin
def provider_verify(request, profile_id):
    """Admin approves or rejects provider"""
    profile = get_object_or_404(UserProfile, id=profile_id, user_type='provider')
    user = profile.user
    
    if request.method == 'POST':
        form = ProviderVerificationForm(request.POST, instance=profile)
        if form.is_valid():
            decision = form.cleaned_data.get('verification_status')
            
            if decision == 'rejected':
                # Hard delete the user and profile
                user_email = user.email
                user.delete()  # This cascades to delete UserProfile too
                messages.success(request, f'Provider {user_email} has been rejected and removed from the system.')
            else:
                # Approve the provider
                profile = form.save()
                notify_provider_verification_update(user, profile.verification_status)
                messages.success(request, f'Provider {profile.verification_status}!')
            
            return redirect('provider_verification_list')
    else:
        form = ProviderVerificationForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'cleaning/admin/provider_approve.html', context)


@require_admin
def service_category_list(request):
    """Admin view to manage service categories"""
    categories = ServiceCategory.objects.all().order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'cleaning/admin/category_list.html', context)


@require_admin
def service_category_create(request):
    """Admin creates new service category"""
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service category created!')
            return redirect('service_category_list')
    else:
        form = ServiceCategoryForm()
    
    context = {
        'form': form,
        'title': 'Create Service Category',
    }
    return render(request, 'cleaning/admin/category_form.html', context)


@require_admin
def service_category_edit(request, category_id):
    """Admin edits service category"""
    category = get_object_or_404(ServiceCategory, id=category_id)
    
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service category updated!')
            return redirect('service_category_list')
    else:
        form = ServiceCategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': 'Edit Service Category',
    }
    return render(request, 'cleaning/admin/category_form.html', context)


@require_admin
def service_category_delete(request, category_id):
    """Admin deletes service category"""
    category = get_object_or_404(ServiceCategory, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Service category deleted!')
        return redirect('service_category_list')
    
    context = {
        'category': category,
    }
    return render(request, 'cleaning/admin/category_confirm_delete.html', context)


@require_admin
def admin_analytics(request):
    # ===== BASIC STATS =====
    total_bookings = Booking.objects.count()
    bookings_this_month = Booking.objects.filter(
        created_at__month=now().month,
        created_at__year=now().year
    ).count()

    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    revenue_this_month = Payment.objects.filter(
        status='completed',
        paid_at__month=now().month,
        paid_at__year=now().year
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_customers = UserProfile.objects.filter(user_type='customer').count()
    total_providers = UserProfile.objects.filter(user_type='provider').count()

    # ===== BOOKINGS BY STATUS =====
    statuses = ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']
    bookings_by_status = {
        status: Booking.objects.filter(status=status).count()
        for status in statuses
    }

    # ===== LAST 6 MONTHS DATA =====
    six_months_ago = now() - timedelta(days=180)

    monthly_bookings_qs = Booking.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    monthly_revenue_qs = Payment.objects.filter(
        status='completed',
        paid_at__gte=six_months_ago
    ).annotate(month=TruncMonth('paid_at')).values('month').annotate(
        amount=Sum('amount')
    ).order_by('month')

    monthly_bookings = [
        {'month': m['month'].strftime('%b'), 'count': m['count']}
        for m in monthly_bookings_qs
    ]

    monthly_revenue = [
        {'month': m['month'].strftime('%b'), 'amount': m['amount'] or 0}
        for m in monthly_revenue_qs
    ]

    # ===== TOP SERVICES =====
    top_services_qs = Booking.objects.values(
        'service__name'
    ).annotate(count=Count('id')).order_by('-count')[:3]

    top_services = [
        {'name': s['service__name'], 'count': s['count']}
        for s in top_services_qs
    ]

    # ===== AVERAGE RATING =====
    average_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0

    # ===== RECENT BOOKINGS =====
    recent_bookings = Booking.objects.select_related(
        'customer', 'service'
    ).order_by('-created_at')[:5]

    context = {
        'total_bookings': total_bookings,
        'bookings_this_month': bookings_this_month,
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        'total_customers': total_customers,
        'total_providers': total_providers,
        'bookings_by_status': bookings_by_status,
        'monthly_bookings': monthly_bookings,
        'monthly_revenue': monthly_revenue,
        'top_services': top_services,
        'average_rating': round(average_rating, 2),
        'recent_bookings': recent_bookings,
    }

    return render(request, 'cleaning/admin/analytics.html', context)


# ======================== PROFILE UPDATE VIEWS ========================

@login_required
def profile_update(request):
    """Update customer/provider profile"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('logged_in_home')
    
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            
            if profile.user_type == 'customer':
                return redirect('user_profile')
            else:
                return redirect('provider_profile')
    else:
        form = UserProfileUpdateForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    if profile.user_type == 'customer':
        template = 'cleaning/customer/profile_update.html'
    else:
        template = 'cleaning/provider_update.html'
    
    return render(request, template, context)


# ======================== PASSWORD RESET VIEWS ========================

from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView
)

class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    template_name = 'cleaning/password_reset.html'
    email_template_name = 'cleaning/emails/password_reset_email.txt'
    html_email_template_name = 'cleaning/emails/password_reset_email.html'
    subject_template_name = 'cleaning/emails/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Password reset done view"""
    template_name = 'cleaning/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirm view"""
    template_name = 'cleaning/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Password reset complete view"""
    template_name = 'cleaning/password_reset_complete.html'

# ======================== ERROR HANDLER VIEWS ========================

def error_404(request, exception=None):
    """Handle 404 - Page Not Found errors"""
    return render(request, 'cleaning/404.html', status=404)



# ======================== INFO PAGES ========================

def contact_view(request):
    """Contact page view"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validation
        if all([name, email, subject, message]):
            # In production, send email here
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'cleaning/contact.html')


def about_view(request):
    """About page view"""
    return render(request, 'cleaning/about.html')


def faq_view(request):
    """FAQ page view"""
    return render(request, 'cleaning/faq.html')

# ======================== NOTIFICATION VIEWS ========================

@login_required
def mark_notification_read(request, notification_id):
    """Mark single notification as read"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'logged_in_home'))


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)
    
    return redirect(request.META.get('HTTP_REFERER', 'logged_in_home'))



# ======================== ERROR HANDLERS ========================

def error_403(request, exception=None):
    """Handle 403 - Permission Denied errors"""
    return render(request, 'cleaning/403.html', status=403)


def error_500(request):
    """Handle 500 - Server Error errors"""
    return render(request, 'cleaning/500.html', status=500)