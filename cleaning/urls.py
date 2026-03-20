from django.urls import path
from . import views

urlpatterns = [
    # ===== AUTHENTICATION =====
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # ===== CUSTOMER ROUTES =====
    path('home/', views.logged_in_home, name='logged_in_home'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('services/', views.services, name='services'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('booking/<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('booking/<int:booking_id>/review/', views.submit_review, name='submit_review'),
    
    # ===== INFO PAGES =====
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('faq/', views.faq_view, name='faq'),
    
    # ===== PROVIDER ROUTES =====
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('provider/job/<int:booking_id>/accept/', views.booking_accept, name='booking_accept'),
    path('provider/job/<int:booking_id>/reject/', views.booking_reject, name='booking_reject'),
    path('provider/job/<int:booking_id>/update/', views.provider_update_job, name='provider_update_job'),
    path('provider/profile/', views.provider_profile, name='provider_profile'),
    
    # ===== ADMIN ROUTES =====
    path('admin/provider-verification/', views.provider_verification_list, name='provider_verification_list'),
    path('admin/provider/<int:profile_id>/verify/', views.provider_verify, name='provider_verify'),
    path('admin/categories/', views.service_category_list, name='service_category_list'),
    path('admin/categories/create/', views.service_category_create, name='service_category_create'),
    path('admin/categories/<int:category_id>/edit/', views.service_category_edit, name='service_category_edit'),
    path('admin/categories/<int:category_id>/delete/', views.service_category_delete, name='service_category_delete'),
]
