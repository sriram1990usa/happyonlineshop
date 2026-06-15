from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product, Category
from reviews.models import Review
from decimal import Decimal

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
        self.user1 = User.objects.create_user(
            email='reviewer1@example.com',
            first_name='Reviewer',
            last_name='One',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            email='reviewer2@example.com',
            first_name='Reviewer',
            last_name='Two',
            password='Password123!'
        )
        self.add_review_url = reverse('reviews:add', kwargs={'product_id': self.product.id})

    def test_add_review_success(self):
        self.client.login(email='reviewer1@example.com', password='Password123!')
        
        # Post a review
        data = {
            'rating': 5,
            'title': 'Excellent quality',
            'body': 'This vase looks absolutely beautiful in my living room. Strongly recommend!'
        }
        response = self.client.post(self.add_review_url, data)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertTrue(res_data['success'])
        
        # Verify db entry
        review = Review.objects.get(user=self.user1, product=self.product)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, 'Excellent quality')
        self.assertEqual(review.body, 'This vase looks absolutely beautiful in my living room. Strongly recommend!')

    def test_duplicate_review_prevention(self):
        self.client.login(email='reviewer1@example.com', password='Password123!')
        
        # Create first review in db
        Review.objects.create(
            product=self.product,
            user=self.user1,
            rating=4,
            title='Good product',
            body='Nice color and finish'
        )
        
        # Post another review for same product by same user
        data = {
            'rating': 5,
            'title': 'Amazing product',
            'body': 'Love it completely'
        }
        response = self.client.post(self.add_review_url, data)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertFalse(res_data['success'])
        self.assertIn('already reviewed', res_data['message'])

    def test_average_rating_calculation(self):
        # Add multiple reviews
        Review.objects.create(product=self.product, user=self.user1, rating=5, title='Great', body='Very good')
        Review.objects.create(product=self.product, user=self.user2, rating=3, title='Okay', body='Decent quality')

        # Check detail page rendering average rating
        detail_url = reverse('products:detail', kwargs={'slug': self.product.slug})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        # Average rating: (5 + 3) / 2 = 4.0
        self.assertEqual(response.context['avg_rating'], 4.0)
