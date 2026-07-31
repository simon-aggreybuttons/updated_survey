from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardAuthFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='dashboard_user',
            email='dashboard@example.com',
            password='secure-pass-123',
            is_staff=True,
            is_superuser=True,
        )

    def test_dashboard_requires_login_and_redirects_after_logout(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/login/', response.url)

        login_response = self.client.post(
            reverse('dashboard_login'),
            {'username': 'dashboard_user', 'password': 'secure-pass-123', 'next': reverse('dashboard_home')},
            follow=True,
        )
        self.assertRedirects(login_response, reverse('dashboard_home'))

        logout_response = self.client.get(reverse('dashboard_logout'), follow=True)
        self.assertRedirects(logout_response, reverse('survey_start'))
