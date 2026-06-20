from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order
from payments.models import Transaction
from decimal import Decimal
import json

User = get_user_model()

@override_settings(RAZORPAY_KEY_ID=None, RAZORPAY_KEY_SECRET=None)
class RazorpayPaymentsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='paymentuser@example.com',
            first_name='Payment',
            last_name='User',
            password='Password123!'
        )
        self.order = Order.objects.create(
            user=self.user,
            shipping_address_snapshot="123 Test St, Bangalore",
            payment_method='RAZORPAY',
            payment_status='PENDING',
            subtotal=Decimal('500.00'),
            discount=Decimal('0.00'),
            shipping_charge=Decimal('0.00'),
            total=Decimal('500.00'),
            status='PENDING'
        )
        # Generate a default mock order ID on setup
        self.order.razorpay_order_id = f"mock_order_{self.order.order_number}"
        self.order.save()

    def test_checkout_view_requires_login(self):
        url = reverse('payments:razorpay_checkout', kwargs={'order_number': self.order.order_number})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_checkout_view_renders_correctly(self):
        self.client.login(email='paymentuser@example.com', password='Password123!')
        url = reverse('payments:razorpay_checkout', kwargs={'order_number': self.order.order_number})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/razorpay_checkout.html')
        self.assertContains(response, self.order.order_number)
        self.assertContains(response, "mock_order_")

    def test_verify_view_success_simulation(self):
        self.client.login(email='paymentuser@example.com', password='Password123!')
        url = reverse('payments:razorpay_verify')
        
        # Test simulated payment success
        payload = {
            'razorpay_payment_id': 'mock_pay_987654321',
            'razorpay_order_id': self.order.razorpay_order_id,
            'razorpay_signature': 'mock_sig_abcdef',
            'is_mock': True
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('redirect_url', data)

        # Verify database updates
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'PAID')
        self.assertEqual(self.order.status, 'CONFIRMED')

        # Check Transaction record
        transaction = Transaction.objects.filter(order=self.order).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.transaction_id, 'mock_pay_987654321')
        self.assertEqual(transaction.status, 'SUCCESS')
        self.assertEqual(transaction.gateway, 'RAZORPAY')

    def test_verify_view_missing_params(self):
        self.client.login(email='paymentuser@example.com', password='Password123!')
        url = reverse('payments:razorpay_verify')
        
        # Payload missing payment ID
        payload = {
            'razorpay_order_id': self.order.razorpay_order_id,
            'is_mock': True
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_webhook_successful_payment(self):
        url = reverse('payments:razorpay_webhook')
        
        # Razorpay payload structure matching payment.captured
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_capture_webhook_123',
                        'order_id': self.order.razorpay_order_id,
                        'amount': 50000,  # in paise
                        'status': 'captured',
                        'notes': {
                            'order_number': self.order.order_number
                        }
                    }
                }
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'PAID')
        self.assertEqual(self.order.status, 'CONFIRMED')
        
        transaction = Transaction.objects.filter(transaction_id='pay_capture_webhook_123').first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, Decimal('500.00'))

