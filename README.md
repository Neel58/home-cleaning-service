# CleanHome Django Project

## Setup Instructions

1. Install Django and Pillow:
```bash
pip install django pillow
```

2. Navigate to the project directory:
```bash
cd cleanhome_project
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Create test data using Django shell:
```bash
python manage.py shell
```

Then paste this code:
```python
from django.contrib.auth.models import User
from cleaning.models import UserProfile, Service

# Create Services
Service.objects.create(name="Deep Cleaning", service_type="deep", description="Full home sanitization including floor scrubbing.", price=999, duration="2-3 Hours", is_best_value=False)
Service.objects.create(name="Sofa Cleaning", service_type="sofa", description="Fabric shampooing and vacuuming.", price=599, duration="1-2 Hours", is_best_value=True)
Service.objects.create(name="Move-In Service", service_type="movein", description="Empty house cleaning before you shift.", price=1499, duration="3-4 Hours", is_best_value=False)

# Create Customer User
customer = User.objects.create_user(username='ab@example.com', email='ab@example.com', password='password123', first_name='a', last_name='b')
UserProfile.objects.create(user=customer, user_type='customer', phone='1234543210')

# Create Provider User
provider = User.objects.create_user(username='provider@example.com', email='provider@example.com', password='password123')
UserProfile.objects.create(user=provider, user_type='provider', phone='9993339992', city='nadiad', experience_years=3, rating=4.8, completed_jobs=142, total_earnings=45000)

exit()
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application:
- Login page: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin

## Test Credentials

**Customer:**
- Email: neel@example.com
- Password: password123

**Provider:**
- Email: provider@example.com
- Password: password123

## Features

### Customer Side
- Login/Authentication
- Browse available services
- View service details with pricing
- Book services with date/time selection
- View profile and booking history
- Manage bookings

### Provider Side
- Login/Authentication
- View new job requests
- Accept/Reject job requests
- View active jobs
- Update job status with notes
- Upload proof of work photos
- View profile with earnings and statistics

## Project Structure
```
cleanhome_project/
├── manage.py
├── cleanhome_project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── cleaning/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── static/cleaning/style.css
    └── templates/cleaning/
        ├── login.html
        ├── index.html
        ├── services.html
        ├── service_detail.html
        ├── user_profile.html
        ├── provider_dashboard.html
        ├── provider_update.html
        └── provider_profile.html
```
