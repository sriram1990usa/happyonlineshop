from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Order, OrderItem
from reviews.models import ProductReview, DeliveryReview, ReviewVote, ReviewReport, AdminReply
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class ReviewsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Home Decor', slug='home-decor')
        self.product = Product.objects.create(
            category=self.category,
            name='Modern Vase',
            price=Decimal('1500.00'),
            stock=5,
            SKU='VASE-MOD-001'
        )
        self.user_purchaser = User.objects.create_user(
            email='purchaser@example.com',
            first_name='Purchaser',
            last_name='One',
            password='Password123!'
        )
        self.user_non_purchaser = User.objects.create_user(
            email='nonpurchaser@example.com',
            first_name='Non',
            last_name='Purchaser',
            password='Password123!'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='Password123!'
        )

        # Create a completed order for purchaser
        self.order = Order.objects.create(
            user=self.user_purchaser,
            status='DELIVERED',
            payment_status='PAID',
            subtotal=Decimal('1500.00'),
            total=Decimal('1500.00'),
            shipping_address_snapshot='123 Test St'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal('1500.00')
        )

        self.add_product_review_url = reverse('reviews:add', kwargs={'product_id': self.product.id})

    def test_purchaser_can_review(self):
        self.client.login(email='purchaser@example.com', password='Password123!')
        data = {
            'rating': 5,
            'title': 'Excellent quality',
            'body': 'This vase looks absolutely beautiful! Strongly recommend!'
        }
        response = self.client.post(self.add_product_review_url, data)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertTrue(res_data['success'])
        
        # Verify db entry
        review = ProductReview.objects.get(user=self.user_purchaser, product=self.product)
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.is_verified_purchase)
        
        # Verify cache update on Product
        self.product.refresh_from_db()
        self.assertEqual(self.product.average_rating, Decimal('5.00'))
        self.assertEqual(self.product.review_count, 1)

    def test_non_purchaser_cannot_review(self):
        self.client.login(email='nonpurchaser@example.com', password='Password123!')
        data = {
            'rating': 3,
            'title': 'Decent',
            'body': 'Decent but I did not buy it.'
        }
        response = self.client.post(self.add_product_review_url, data)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertFalse(res_data['success'])
        self.assertIn('Only verified purchasers', res_data['message'])
        self.assertFalse(ProductReview.objects.filter(user=self.user_non_purchaser, product=self.product).exists())

    def test_duplicate_review_prevention(self):
        self.client.login(email='purchaser@example.com', password='Password123!')
        ProductReview.objects.create(
            product=self.product,
            user=self.user_purchaser,
            rating=5,
            title='First',
            body='First review comment.',
            status='APPROVED'
        )
        
        data = {
            'rating': 4,
            'title': 'Second',
            'body': 'Duplicate attempt.'
        }
        response = self.client.post(self.add_product_review_url, data)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertFalse(res_data['success'])
        self.assertIn('already reviewed', res_data['message'])

    def test_delivery_review_conditions(self):
        self.client.login(email='purchaser@example.com', password='Password123!')
        add_delivery_url = reverse('reviews:add_delivery_review', kwargs={'order_number': self.order.order_number})
        data = {
            'rating': 5,
            'body': 'Very fast shipping, excellent packaging.'
        }
        response = self.client.post(add_delivery_url, data)
        self.assertEqual(response.status_code, 302)
        
        del_review = DeliveryReview.objects.get(order=self.order, user=self.user_purchaser)
        self.assertEqual(del_review.rating, 5)

        response_dup = self.client.post(add_delivery_url, data)
        self.assertEqual(response_dup.status_code, 200)
        self.assertContains(response_dup, "already been reviewed")

    def test_edit_and_delete_permissions(self):
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user_purchaser,
            rating=5,
            title='Great',
            body='Nice',
            status='APPROVED'
        )
        
        edit_url = reverse('reviews:edit_product_review', kwargs={'pk': review.id})
        delete_url = reverse('reviews:delete_product_review', kwargs={'pk': review.id})
        
        # Non-owner tries to edit
        self.client.login(email='nonpurchaser@example.com', password='Password123!')
        response_edit = self.client.get(edit_url)
        self.assertEqual(response_edit.status_code, 403)
        
        # Owner can edit
        self.client.login(email='purchaser@example.com', password='Password123!')
        response_edit_ok = self.client.get(edit_url)
        self.assertEqual(response_edit_ok.status_code, 200)
        
        # Admin can delete
        self.client.login(email='admin@example.com', password='Password123!')
        response_delete_ok = self.client.post(delete_url)
        self.assertEqual(response_delete_ok.status_code, 302)
        self.assertFalse(ProductReview.objects.filter(pk=review.id).exists())

    def test_admin_reply_creation(self):
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user_purchaser,
            rating=5,
            title='Great',
            body='Nice',
            status='APPROVED'
        )
        admin_reply = AdminReply.objects.create(
            product_review=review,
            admin=self.admin,
            body="Thank you for your feedback!"
        )
        self.assertEqual(review.admin_reply, admin_reply)
        self.assertEqual(admin_reply.body, "Thank you for your feedback!")

    def test_rating_calculations(self):
        ProductReview.objects.create(product=self.product, user=self.user_purchaser, rating=5, title='R1', body='B1', status='APPROVED')
        ProductReview.objects.create(product=self.product, user=self.user_non_purchaser, rating=3, title='R2', body='B2', status='APPROVED')

        self.product.refresh_from_db()
        self.assertEqual(self.product.average_rating, Decimal('4.00'))
        self.assertEqual(self.product.review_count, 2)

    def test_review_moderation_workflow(self):
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user_purchaser,
            rating=5,
            title='R1',
            body='B1',
            status='PENDING'
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.average_rating, Decimal('0.00'))
        self.assertEqual(self.product.review_count, 0)
        
        review.status = 'APPROVED'
        review.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.average_rating, Decimal('5.00'))
        self.assertEqual(self.product.review_count, 1)
