from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class AccountAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        resp = self.client.post('/api/auth/register/', {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'name': 'John Doe'
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['first_name'], 'John')

    def test_login_with_username_and_email(self):
        User.objects.create_user(
            username='janedoe',
            email='jane@example.com',
            password='securepassword',
            first_name='Jane',
            last_name='Doe'
        )

        # Login with username
        resp1 = self.client.post('/api/auth/login/', {
            'username': 'janedoe',
            'password': 'securepassword'
        }, format='json')
        self.assertEqual(resp1.status_code, 200)
        self.assertIn('token', resp1.data)
        self.assertEqual(resp1.data['user']['first_name'], 'Jane')

        # Login with email
        resp2 = self.client.post('/api/auth/login/', {
            'username': 'jane@example.com',
            'password': 'securepassword'
        }, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('token', resp2.data)

    def test_login_invalid_credentials(self):
        resp = self.client.post('/api/auth/login/', {
            'username': 'nonexistent',
            'password': 'wrong'
        }, format='json')
        self.assertEqual(resp.status_code, 401)
