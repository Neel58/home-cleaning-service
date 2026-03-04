from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from cleaning.models import ServiceCategory, Service, UserProfile, Booking, Review, Payment
import random

class Command(BaseCommand):
    help = 'Seed the database with dummy cleaning service data'

    def handle(self, *args, **options):
        self.stdout.write('Starting data seeding...')
        
        # Clear existing data
        self.clear_data()
        
        # Create service categories
        self.create_service_categories()
        
        # Create users
        self.create_users()
        
        # Create services
        self.create_services()
        
        # Create bookings and reviews
        self.create_bookings_and_reviews()
        
        self.stdout.write(self.style.SUCCESS('✓ Data seeding completed successfully!'))

    def clear_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        Payment.objects.all().delete()
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Service.objects.all().delete()
        ServiceCategory.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(username__startswith='customer_').delete()
        User.objects.filter(username__startswith='provider_').delete()
        User.objects.filter(username='admin').delete()

    def create_service_categories(self):
        """Create cleaning service categories"""
        self.stdout.write('Creating service categories...')
        
        categories_data = [
            {
                'name': 'Wall Cleaning',
                'description': 'Professional wall cleaning for residential and commercial spaces',
                'base_price': 50.00,
            },
            {
                'name': 'Sofa Cleaning',
                'description': 'Expert sofa and upholstered furniture cleaning',
                'base_price': 75.00,
            },
            {
                'name': 'Carpet Cleaning',
                'description': 'Deep carpet cleaning and stain removal',
                'base_price': 100.00,
            },
            {
                'name': 'Kitchen Cleaning',
                'description': 'Thorough kitchen cleaning including appliances',
                'base_price': 80.00,
            },
            {
                'name': 'Bathroom Cleaning',
                'description': 'Complete bathroom sanitization and cleaning',
                'base_price': 60.00,
            },
            {
                'name': 'Deep Cleaning',
                'description': 'Comprehensive deep cleaning of entire spaces',
                'base_price': 150.00,
            },
            {
                'name': 'Window Cleaning',
                'description': 'Interior and exterior window cleaning services',
                'base_price': 45.00,
            },
            {
                'name': 'Upholstery Cleaning',
                'description': 'Specialized cleaning for chairs, cushions, and fabric items',
                'base_price': 70.00,
            },
        ]
        
        for category_data in categories_data:
            ServiceCategory.objects.create(**category_data)
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(categories_data)} service categories'))

    def create_users(self):
        """Create sample customers and providers"""
        self.stdout.write('Creating users...')
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@cleanhome.com',
            password='admin123'
        )
        
        # Create customers
        customers_data = [
            {'username': 'customer_john', 'email': 'john@example.com', 'password': 'pass123'},
            {'username': 'customer_sarah', 'email': 'sarah@example.com', 'password': 'pass123'},
            {'username': 'customer_mike', 'email': 'mike@example.com', 'password': 'pass123'},
        ]
        

        for customer_data in customers_data:
            user = User.objects.create_user(
                username=customer_data['username'],
                email=customer_data['email'],
                password=customer_data['password'],
                first_name=customer_data['username'].split('_')[1].capitalize()
            )
            UserProfile.objects.create(
                user=user,
                user_type='customer',
                phone=f'555-{random.randint(1000, 9999)}',
                city=random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston']),
                verification_status='verified'
            )
        
        # Create providers
        providers_data = [
            {'username': 'provider_alex', 'email': 'alex@provider.com', 'password': 'pass123'},
            {'username': 'provider_emma', 'email': 'emma@provider.com', 'password': 'pass123'},
            {'username': 'provider_david', 'email': 'david@provider.com', 'password': 'pass123'},
        ]
        
        for provider_data in providers_data:
            user = User.objects.create_user(
                username=provider_data['username'],
                email=provider_data['email'],
                password=provider_data['password'],
                first_name=provider_data['username'].split('_')[1].capitalize()
            )
            UserProfile.objects.create(
                user=user,
                user_type='provider',
                phone=f'555-{random.randint(1000, 9999)}',
                city=random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston']),
                experience_years=random.randint(2, 10),
                verification_status='verified',
                is_verified_by_admin=True
            )
        
        self.stdout.write(self.style.SUCCESS(f'  Created 3 customers and 3 providers'))

    def create_services(self):
        """Create services under each category"""
        self.stdout.write('Creating services...')
        
        services_data = [
            # Wall Cleaning
            {
                'category_name': 'Wall Cleaning',
                'services': [
                    {'name': 'Standard Wall Cleaning', 'service_type': 'deep', 'price': 50.00, 'duration': '2-3 hours'},
                    {'name': 'Paint Refresh Wall Cleaning', 'service_type': 'deep', 'price': 75.00, 'duration': '3-4 hours', 'is_best_value': True},
                    {'name': 'Stain Removal Walls', 'service_type': 'deep', 'price': 65.00, 'duration': '2.5 hours'},
                ]
            },
            # Sofa Cleaning
            {
                'category_name': 'Sofa Cleaning',
                'services': [
                    {'name': 'Single Sofa Cleaning', 'service_type': 'sofa', 'price': 75.00, 'duration': '1-2 hours'},
                    {'name': 'Large Sectional Sofa Cleaning', 'service_type': 'sofa', 'price': 120.00, 'duration': '2-3 hours', 'is_best_value': True},
                    {'name': 'Sofa + Chair Combo', 'service_type': 'sofa', 'price': 130.00, 'duration': '2.5-3.5 hours'},
                ]
            },
            # Carpet Cleaning
            {
                'category_name': 'Carpet Cleaning',
                'services': [
                    {'name': 'Room Carpet Cleaning', 'service_type': 'deep', 'price': 100.00, 'duration': '2 hours'},
                    {'name': 'Whole House Carpet Cleaning', 'service_type': 'deep', 'price': 250.00, 'duration': '4-5 hours', 'is_best_value': True},
                    {'name': 'Pet Stain Removal', 'service_type': 'deep', 'price': 125.00, 'duration': '2.5 hours'},
                ]
            },
            # Kitchen Cleaning
            {
                'category_name': 'Kitchen Cleaning',
                'services': [
                    {'name': 'Kitchen Basic Cleaning', 'service_type': 'deep', 'price': 80.00, 'duration': '2 hours'},
                    {'name': 'Deep Kitchen Cleaning', 'service_type': 'deep', 'price': 130.00, 'duration': '3-4 hours', 'is_best_value': True},
                    {'name': 'Oven & Appliance Intensive', 'service_type': 'deep', 'price': 110.00, 'duration': '2.5 hours'},
                ]
            },
            # Bathroom Cleaning
            {
                'category_name': 'Bathroom Cleaning',
                'services': [
                    {'name': 'Standard Bathroom Cleaning', 'service_type': 'deep', 'price': 60.00, 'duration': '1.5 hours'},
                    {'name': 'Deluxe Bathroom Cleaning', 'service_type': 'deep', 'price': 95.00, 'duration': '2.5 hours', 'is_best_value': True},
                    {'name': 'Multiple Bathrooms Package', 'service_type': 'deep', 'price': 150.00, 'duration': '3-4 hours'},
                ]
            },
            # Deep Cleaning
            {
                'category_name': 'Deep Cleaning',
                'services': [
                    {'name': 'Apartment Deep Clean', 'service_type': 'deep', 'price': 200.00, 'duration': '4 hours'},
                    {'name': 'House Deep Clean', 'service_type': 'movein', 'price': 350.00, 'duration': '6-7 hours', 'is_best_value': True},
                    {'name': 'Move-In/Out Deep Clean', 'service_type': 'movein', 'price': 400.00, 'duration': '7-8 hours'},
                ]
            },
            # Window Cleaning
            {
                'category_name': 'Window Cleaning',
                'services': [
                    {'name': 'Interior Windows Only', 'service_type': 'deep', 'price': 45.00, 'duration': '1.5 hours'},
                    {'name': 'Interior & Exterior Windows', 'service_type': 'deep', 'price': 75.00, 'duration': '2.5 hours', 'is_best_value': True},
                    {'name': 'Window + Frame & Track Cleaning', 'service_type': 'deep', 'price': 100.00, 'duration': '3 hours'},
                ]
            },
            # Upholstery Cleaning
            {
                'category_name': 'Upholstery Cleaning',
                'services': [
                    {'name': 'Single Chair Upholstery', 'service_type': 'deep', 'price': 70.00, 'duration': '1.5 hours'},
                    {'name': 'Sofa + 2 Chairs Upholstery', 'service_type': 'deep', 'price': 150.00, 'duration': '3 hours', 'is_best_value': True},
                    {'name': 'Full Living Room Upholstery', 'service_type': 'deep', 'price': 200.00, 'duration': '4 hours'},
                ]
            },
        ]
        
        total_services = 0
        for service_group in services_data:
            category = ServiceCategory.objects.get(name=service_group['category_name'])
            for service_info in service_group['services']:
                Service.objects.create(
                    category=category,
                    name=service_info['name'],
                    service_type=service_info['service_type'],
                    description=f"Professional {service_info['name'].lower()} service for your home",
                    price=service_info['price'],
                    duration=service_info['duration'],
                    is_best_value=service_info.get('is_best_value', False),
                )
                total_services += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {total_services} services'))

    def create_bookings_and_reviews(self):
        """Create sample bookings with reviews"""
        self.stdout.write('Creating bookings and reviews...')
        
        customers = User.objects.filter(username__startswith='customer_')
        providers = User.objects.filter(username__startswith='provider_')
        services = Service.objects.all()
        
        booking_count = 0
        review_count = 0
        payment_count = 0
        
        # Create completed bookings with reviews
        for i in range(5):
            customer = random.choice(customers)
            provider = random.choice(providers)
            service = random.choice(services)
            
            # Past booking (completed)
            booking = Booking.objects.create(
                customer=customer,
                provider=provider,
                service=service,
                date_time=timezone.now() - timedelta(days=random.randint(1, 30)),
                location=f'{random.randint(100, 999)} Main St, City',
                status='completed',
                payment_status='paid',
                notes='Great service needed'
            )
            booking_count += 1
            
            # Add review
            review = Review.objects.create(
                booking=booking,
                rating=random.randint(4, 5),
                comment=random.choice([
                    'Excellent service! Very professional and thorough.',
                    'Great job! Would book again.',
                    'Very satisfied with the cleaning quality.',
                    'Highly recommended! Professional and punctual.',
                    'Outstanding service! Better than expected.',
                ])
            )
            review_count += 1
            
            # Add payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=service.price,
                payment_gateway='stripe',
                transaction_id=f'txn_{booking.id}_{random.randint(10000, 99999)}',
                status='completed',
                paid_at=booking.date_time + timedelta(hours=1)
            )
            payment_count += 1
        
        # Create pending bookings
        for i in range(3):
            customer = random.choice(customers)
            service = random.choice(services)
            
            booking = Booking.objects.create(
                customer=customer,
                service=service,
                date_time=timezone.now() + timedelta(days=random.randint(1, 7)),
                location=f'{random.randint(100, 999)} Main St, City',
                status='pending',
                payment_status='pending',
                notes='Needs urgent cleaning'
            )
            booking_count += 1
        
        # Create confirmed bookings
        for i in range(2):
            customer = random.choice(customers)
            provider = random.choice(providers)
            service = random.choice(services)
            
            booking = Booking.objects.create(
                customer=customer,
                provider=provider,
                service=service,
                date_time=timezone.now() + timedelta(days=random.randint(2, 5)),
                location=f'{random.randint(100, 999)} Main St, City',
                status='confirmed',
                payment_status='paid',
                notes='Standard cleaning'
            )
            booking_count += 1
            
            # Add payment record for confirmed bookings
            payment = Payment.objects.create(
                booking=booking,
                amount=service.price,
                payment_gateway='stripe',
                transaction_id=f'txn_{booking.id}_{random.randint(10000, 99999)}',
                status='completed',
                paid_at=timezone.now()
            )
            payment_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {booking_count} bookings'))
        self.stdout.write(self.style.SUCCESS(f'  Created {review_count} reviews'))
        self.stdout.write(self.style.SUCCESS(f'  Created {payment_count} payments'))
