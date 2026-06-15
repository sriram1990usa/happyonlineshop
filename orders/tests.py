from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product, Category
from cart.models import Cart, CartItem, Coupon
from accounts.models import Address
from orders.models import Order, OrderItem
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class OrdersTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Home', slug='home')
        self.product = Product.objects.create(
            category=self.category,
            name='Coffee Mug',
            price=Decimal('500.00'),
            stock=10,
            SKU='MUG-COFFEE-001'
        )
        self.user = User.objects.create_user(
            email='orderuser@example.com',
            first_name='Order',
            last_name='User',
            password='Password123!'
        )
        self.address = Address.objects.create(
            user=self.user,
            recipient_name='Home Recipient',
            phone_number='1234567890',
            street_address='100 Park Ave',
            city='Bangalore',
            state='Karnataka',
            postal_code='560001',
            country='IN',
            address_type='HOME',
            is_default=True
        )
        self.address_url = reverse('orders:checkout_address')
        self.payment_url = reverse('orders:checkout_payment')

    def test_checkout_address_view(self):
        self.client.login(email='orderuser@example.com', password='Password123!')
        
        # When cart is empty, should redirect to cart details
        response = self.client.get(self.address_url)
        self.assertEqual(response.status_code, 302)

        # Add item to cart
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        # Retrieve address selection page
        response = self.client.get(self.address_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home Recipient')

        # Select address
        response = self.client.post(self.address_url, {'address_id': self.address.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['checkout_address_id'], str(self.address.id))

    def test_checkout_payment_and_order_creation(self):
        self.client.login(email='orderuser@example.com', password='Password123!')
        
        # Populate session and cart
        session = self.client.session
        session['checkout_address_id'] = str(self.address.id)
        session.save()
        
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        # Get payment page
        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        # Total = subtotal (2 * 500) + shipping (0.00 since subtotal >= 500) = 1000.00
        self.assertEqual(response.context['total'], Decimal('1000.00'))

        # Place order using Cash On Delivery (COD)
        response = self.client.post(self.payment_url, {'payment_method': 'COD'})
        self.assertEqual(response.status_code, 302)

        # Verify order creation
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_method, 'COD')
        self.assertEqual(order.payment_status, 'PENDING')
        self.assertEqual(order.status, 'CONFIRMED')
        self.assertEqual(order.total, Decimal('1000.00'))

        # Verify stock decrement
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)  # 10 - 2 = 8

        # Verify cart cleared
        self.assertEqual(cart.items.count(), 0)
