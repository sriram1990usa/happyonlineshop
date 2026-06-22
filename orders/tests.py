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

    def test_generate_and_download_invoice(self):
        # Create an order
        order = Order.objects.create(
            user=self.user,
            shipping_address_snapshot="Home Recipient\n100 Park Ave\nBangalore, Karnataka - 560001",
            payment_method='COD',
            payment_status='PAID',
            subtotal=Decimal('500.00'),
            total=Decimal('500.00')
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal('500.00')
        )
        
        # Test PDF generation service
        from .invoice_service import generate_invoice_pdf
        pdf_data = generate_invoice_pdf(order)
        self.assertIsNotNone(pdf_data)
        self.assertTrue(len(pdf_data) > 0)
        
        # Log in and test invoice download view
        self.client.login(email='orderuser@example.com', password='Password123!')
        url = reverse('orders:order_invoice', kwargs={'order_number': order.order_number})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f'attachment; filename="Invoice-{order.order_number}.pdf"', response['Content-Disposition'])

    def test_order_tracking_updates(self):
        # Create an order
        order = Order.objects.create(
            user=self.user,
            shipping_address_snapshot="Home Recipient\n100 Park Ave\nBangalore, Karnataka - 560001",
            payment_method='COD',
            payment_status='PAID',
            subtotal=Decimal('500.00'),
            total=Decimal('500.00'),
            status='CONFIRMED'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal('500.00')
        )

        # Make staff user for dashboard access
        self.staff_user = User.objects.create_superuser(
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User',
            password='AdminPassword123!'
        )
        self.client.login(email='adminuser@example.com', password='AdminPassword123!')

        # Post update to SHIPPED
        dashboard_url = reverse('dashboard:orders')
        response = self.client.post(dashboard_url, {
            'order_id': order.id,
            'status': 'SHIPPED',
            'courier_name': 'BlueDart Express',
            'tracking_number': 'BD871625',
            'tracking_url': 'https://bluedart.com/track/BD871625'
        })
        self.assertEqual(response.status_code, 302) # redirects back to orders list
        
        # Verify database fields updated
        order.refresh_from_db()
        self.assertEqual(order.status, 'SHIPPED')
        self.assertEqual(order.courier_name, 'BlueDart Express')
        self.assertEqual(order.tracking_number, 'BD871625')
        self.assertEqual(order.tracking_url, 'https://bluedart.com/track/BD871625')
        self.assertIsNotNone(order.shipped_at)

        # Post update to DELIVERED
        response = self.client.post(dashboard_url, {
            'order_id': order.id,
            'status': 'DELIVERED',
            'delivery_proof_notes': 'Delivered to security gate, signed by officer Raj'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify database fields updated
        order.refresh_from_db()
        self.assertEqual(order.status, 'DELIVERED')
        self.assertEqual(order.delivery_proof_notes, 'Delivered to security gate, signed by officer Raj')
        self.assertIsNotNone(order.delivered_at)

        # Log in as user and fetch details page to verify rendering
        self.client.login(email='orderuser@example.com', password='Password123!')
        detail_url = reverse('orders:detail', kwargs={'order_number': order.order_number})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shipment & Delivery Details')
        self.assertContains(response, 'BlueDart Express')
        self.assertContains(response, 'BD871625')
        self.assertContains(response, 'Delivered to security gate, signed by officer Raj')
