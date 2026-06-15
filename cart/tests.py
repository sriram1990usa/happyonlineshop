from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product, Category
from cart.models import Cart, CartItem, Coupon
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()

class CartTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Apparel', slug='apparel')
        self.product = Product.objects.create(
            category=self.category,
            name='Premium Cotton Tee',
            price=Decimal('1000.00'),
            stock=10,
            SKU='TEE-COTTON-001'
        )
        self.user = User.objects.create_user(
            email='cartuser@example.com',
            first_name='Cart',
            last_name='User',
            password='Password123!'
        )
        self.add_url = reverse('cart:add')
        self.detail_url = reverse('cart:detail')
        self.apply_coupon_url = reverse('cart:apply_coupon')

    def test_add_to_cart_authenticated(self):
        self.client.login(email='cartuser@example.com', password='Password123!')
        
        # Add product to cart
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        # The view AddToCartView expects JSON POST or form POST.
        # Let's inspect AddToCartView's code structure by sending standard POST.
        response = self.client.post(self.add_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertTrue(res_data['success'])
        
        # Verify db cart structure
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart.subtotal, Decimal('2000.00'))

    def test_update_and_remove_cart_item(self):
        self.client.login(email='cartuser@example.com', password='Password123!')
        
        # First add
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        # Update item quantity
        update_url = reverse('cart:update', kwargs={'item_id': item.id})
        response = self.client.post(update_url, data=json.dumps({'quantity': 5}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

        # Remove item
        remove_url = reverse('cart:remove', kwargs={'item_id': item.id})
        response = self.client.post(remove_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cart.items.count(), 0)

    def test_coupon_calculations(self):
        now = timezone.now()
        coupon_percent = Coupon.objects.create(
            code='SAVE10',
            discount_type='PERCENT',
            value=Decimal('10.00'),
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            active=True
        )
        coupon_fixed = Coupon.objects.create(
            code='SAVE100',
            discount_type='FIXED',
            value=Decimal('100.00'),
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            active=True,
            min_purchase_amount=Decimal('500.00')
        )

        subtotal = Decimal('1000.00')
        self.assertTrue(coupon_percent.is_valid(subtotal))
        self.assertEqual(coupon_percent.calculate_discount(subtotal), Decimal('100.00'))

        self.assertTrue(coupon_fixed.is_valid(subtotal))
        self.assertEqual(coupon_fixed.calculate_discount(subtotal), Decimal('100.00'))

        # Minimum purchase check
        low_subtotal = Decimal('300.00')
        self.assertFalse(coupon_fixed.is_valid(low_subtotal))
