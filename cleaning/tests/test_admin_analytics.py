from django.test import TestCase, Client
from django.contrib.auth.models import User


class AdminAnalyticsDummyDataTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_admin_analytics_displays_dummy_data_when_db_empty(self):
        response = self.client.get('/dashboard/analytics/')
        self.assertEqual(response.status_code, 200)

        # Confirm dummy behavior is signaled in context
        self.assertTrue(response.context.get('is_dummy_data', False))

        # Confirm 6-month fallback is used
        monthly_bookings = response.context['monthly_bookings']
        monthly_revenue = response.context['monthly_revenue']
        self.assertEqual(len(monthly_bookings), 6)
        self.assertEqual(len(monthly_revenue), 6)

        # Confirm status data fallback is used
        status_data = response.context['bookings_by_status']
        self.assertEqual(status_data.get('completed'), 12)
        self.assertEqual(status_data.get('cancelled'), 1)

        # Confirm top services fallback is used
        top_services = response.context['top_services']
        self.assertGreaterEqual(len(top_services), 3)
        self.assertEqual(top_services[0]['name'], 'Full House Cleaning')
