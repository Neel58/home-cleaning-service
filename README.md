<div align="center">

<br/>

```
 ██████╗██╗     ███████╗ █████╗ ███╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗
██╔════╝██║     ██╔════╝██╔══██╗████╗  ██║██║  ██║██╔═══██╗████╗ ████║██╔════╝
██║     ██║     █████╗  ███████║██╔██╗ ██║███████║██║   ██║██╔████╔██║█████╗  
██║     ██║     ██╔══╝  ██╔══██║██║╚██╗██║██╔══██║██║   ██║██║╚██╔╝██║██╔══╝  
╚██████╗███████╗███████╗██║  ██║██║ ╚████║██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗
 ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝
```

### *Professional Home Cleaning — Booked in Minutes.*

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<br/>

[Features](#-features) · [Quick Start](#-quick-start) · [Project Structure](#-project-structure) · [Test Credentials](#-test-credentials)

<br/>

</div>

---

## 🌟 Overview

**CleanHome** is a full-stack Django web application that bridges the gap between homeowners and professional cleaners. Customers can browse services, book appointments, and track job progress — while providers manage their pipeline, upload work proofs, and monitor earnings — all in one place.

> Built with Django · Designed for simplicity · Ready to extend

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 👤 Customer
- 🔐 Login & Authentication
- 🧹 Browse available cleaning services
- 📋 View service details with pricing & duration
- 📅 Book services with date/time selection
- 📦 View booking history & manage bookings
- 👤 Personal profile management

</td>
<td width="50%">

### 🔧 Provider
- 🔐 Login & Authentication
- 📥 View & respond to job requests
- ✅ Accept or reject incoming bookings
- 🔄 Update job status with progress notes
- 📸 Upload proof-of-work photos
- 📊 Dashboard with earnings & job statistics

</td>
</tr>
</table>

---

## ⚡ Quick Start

### Prerequisites

- Python **3.8+**
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/Neel58/home-cleaning-service.git
cd home-cleaning-service
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> Or manually: `pip install django pillow`

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a Superuser

```bash
python manage.py createsuperuser
```

### 5. Seed Test Data

```bash
python manage.py shell
```

Paste the following into the shell:

```python
from django.contrib.auth.models import User
from cleaning.models import UserProfile, Service

# Services
Service.objects.create(name="Deep Cleaning",   service_type="deep",   description="Full home sanitization including floor scrubbing.", price=999,  duration="2-3 Hours", is_best_value=False)
Service.objects.create(name="Sofa Cleaning",   service_type="sofa",   description="Fabric shampooing and vacuuming.",                  price=599,  duration="1-2 Hours", is_best_value=True)
Service.objects.create(name="Move-In Service", service_type="movein", description="Empty house cleaning before you shift.",             price=1499, duration="3-4 Hours", is_best_value=False)

# Customer
customer = User.objects.create_user(username='neel@example.com', email='neel@example.com', password='password123', first_name='Neel', last_name='Shah')
UserProfile.objects.create(user=customer, user_type='customer', phone='91 98765 43210')

# Provider
provider = User.objects.create_user(username='provider@example.com', email='provider@example.com', password='password123')
UserProfile.objects.create(user=provider, user_type='provider', phone='91 98765 43210', city='Vadodara', experience_years=3, rating=4.8, completed_jobs=142, total_earnings=45000)

exit()
```

### 6. Start the Server

```bash
python manage.py runserver
```

---

## 🔑 Test Credentials

> ⚠️ **For local development only.** Never use these in production.

| Role | Email | Password |
|------|-------|----------|
| 👤 Customer | `neel@example.com` | `password123` |
| 🔧 Provider | `provider@example.com` | `password123` |
| 🛡️ Admin Panel | `/admin` | *(superuser credentials)* |

**URLs:**
- App → http://127.0.0.1:8000/
- Admin → http://127.0.0.1:8000/admin

---

## 📁 Project Structure

```
home-cleaning-service/
│
├── manage.py
├── requirements.txt
│
├── cleanhome_project/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── cleaning/                   # Main application
    ├── models.py               # UserProfile, Service, Booking
    ├── views.py                # All view logic
    ├── urls.py                 # App URL routing
    ├── admin.py                # Admin panel config
    │
    ├── static/cleaning/
    │   └── style.css
    │
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

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Django |
| Frontend | HTML5, CSS3 |
| Database | SQLite (dev) |
| Media | Pillow |

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

```bash
# Fork → Clone → Branch → Commit → PR
git checkout -b feature/your-feature-name
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

Made with by [Neel58](https://github.com/Neel58) and Rahul08(https://github.com/solankirahul08)

</div>
