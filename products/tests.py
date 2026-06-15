from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from products.models import Product, Category, Brand, ProductVariant
from decimal import Decimal

class ProductsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.brand = Brand.objects.create(name='Sony', slug='sony')
        
        # Product with discount
        self.product_discount = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name='Sony WH-1000XM4',
            price=Decimal('24990.00'),
            discount_price=Decimal('19990.00'),
            stock=10,
            is_active=True,
            SKU='SONY-XM4-001'
        )

        # Product without discount
        self.product_regular = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name='Sony WH-CH510',
            price=Decimal('3990.00'),
            stock=15,
            is_active=True,
            SKU='SONY-CH510-002'
        )

        # Add a product variant
        self.variant = ProductVariant.objects.create(
            product=self.product_discount,
            name='Color',
            value='Black',
            price_override=Decimal('20990.00'),
            stock=5
        )

    def test_product_price_calculations(self):
        # Product with discount
        self.assertEqual(self.product_discount.current_price, Decimal('19990.00'))
        self.assertTrue(self.product_discount.has_discount)
        self.assertEqual(self.product_discount.discount_percentage, 20)  # (24990-19990)/24990 = 20%

        # Product without discount
        self.assertEqual(self.product_regular.current_price, Decimal('3990.00'))
        self.assertFalse(self.product_regular.has_discount)
        self.assertEqual(self.product_regular.discount_percentage, 0)

    def test_product_slug_auto_generation(self):
        product = Product.objects.create(
            category=self.category,
            name='Test Auto Slug Name',
            price=Decimal('100.00'),
            stock=1,
            SKU='AUTO-SLUG-001'
        )
        self.assertEqual(product.slug, slugify('Test Auto Slug Name'))

    def test_product_list_view(self):
        url = reverse('products:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sony WH-1000XM4')
        self.assertContains(response, 'Sony WH-CH510')

    def test_product_list_filtering(self):
        url = reverse('products:list')
        
        # Filter by category
        response = self.client.get(url, {'category': 'electronics'})
        self.assertEqual(len(response.context['products']), 2)

        # Filter by brand
        response = self.client.get(url, {'brand': 'sony'})
        self.assertEqual(len(response.context['products']), 2)

        # Filter by max price
        response = self.client.get(url, {'max_price': '5000.00'})
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].name, 'Sony WH-CH510')

    def test_product_detail_view(self):
        url = reverse('products:detail', kwargs={'slug': self.product_discount.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'], self.product_discount)
        self.assertIn(self.variant, response.context['variants'])
