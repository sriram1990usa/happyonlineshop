from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Address

User = get_user_model()

class AccountsTestCase(TestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.profile_url = reverse('accounts:profile')
        self.address_url = reverse('accounts:addresses')
        
        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!'
        }
        self.user = User.objects.create_user(
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            password='ExistingPassword123!'
        )

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)  # Should redirect to home
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())
        # Ensure email is set as username
        new_user = User.objects.get(email='testuser@example.com')
        self.assertEqual(new_user.username, 'testuser@example.com')

    def test_user_registration_password_mismatch(self):
        data = self.user_data.copy()
        data['password2'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)  # Renders form again with errors
        self.assertFalse(User.objects.filter(email='testuser@example.com').exists())

    def test_user_login(self):
        login_data = {
            'email': 'existing@example.com',
            'password': 'ExistingPassword123!'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 302)
        # Check authentication state via session
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_profile_update(self):
        self.client.login(email='existing@example.com', password='ExistingPassword123!')
        profile_data = {
            'phone_number': '+919876543210',
        }
        response = self.client.post(self.profile_url, profile_data)
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone_number, '+919876543210')

    def test_address_management(self):
        self.client.login(email='existing@example.com', password='ExistingPassword123!')
        address_data = {
            'recipient_name': 'Home Address',
            'phone_number': '1234567890',
            'street_address': '123 Main St',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'postal_code': '560001',
            'country': 'IN',
            'address_type': 'HOME',
            'is_default': True
        }
        # Create address
        response = self.client.post(self.address_url, address_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Address.objects.filter(user=self.user, city='Bangalore').exists())
        
        # Delete address
        address = Address.objects.get(user=self.user, city='Bangalore')
        delete_url = reverse('accounts:delete_address', kwargs={'pk': address.pk})
        delete_response = self.client.post(delete_url)
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Address.objects.filter(user=self.user, city='Bangalore').exists())
