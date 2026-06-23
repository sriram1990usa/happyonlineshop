import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'premiumshop.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Profile, Address
from products.models import Category, Brand, Product, ProductVariant, ProductImage
from cart.models import Coupon
from reviews.models import ProductReview
from notifications.models import Notification

User = get_user_model()

def seed():
    print("Starting database seeding...")

    # 1. Clean existing data
    print("Cleaning existing tables...")
    Notification.objects.all().delete()
    ProductReview.objects.all().delete()
    Coupon.objects.all().delete()
    ProductVariant.objects.all().delete()
    ProductImage.objects.all().delete()
    Product.objects.all().delete()
    Brand.objects.all().delete()
    Category.objects.all().delete()
    Address.objects.all().delete()
    User.objects.all().delete()

    # 2. Create Users
    print("Creating admin and customer accounts...")
    admin_user = User.objects.create_superuser(
        email='admin@premiumshop.ai',
        first_name='Shop',
        last_name='Admin',
        password='AdminPass123!'
    )
    admin_user.username = admin_user.email
    admin_user.save()

    customer_user = User.objects.create_user(
        email='customer@premiumshop.ai',
        first_name='Jane',
        last_name='Doe',
        password='CustomerPass123!'
    )
    customer_user.username = customer_user.email
    customer_user.save()

    reviewer_user = User.objects.create_user(
        email='reviewer@premiumshop.ai',
        first_name='Alex',
        last_name='Smith',
        password='ReviewPass123!'
    )
    reviewer_user.username = reviewer_user.email
    reviewer_user.save()

    # 3. Create Addresses
    print("Adding default address...")
    Address.objects.create(
        user=customer_user,
        recipient_name='Jane Doe',
        phone_number='+919876543210',
        street_address='Flat 405, Block B, Prestige Heights, Outer Ring Road',
        city='Bangalore',
        state='Karnataka',
        postal_code='560103',
        country='IN',
        address_type='HOME',
        is_default=True
    )

    # 4. Create Categories
    print("Creating categories...")
    electronics = Category.objects.create(name='Electronics', slug='electronics', is_featured=True, description='Phones, laptops, headphones, and more.')
    fashion = Category.objects.create(name='Fashion', slug='fashion', is_featured=True, description='Premium clothing, footwear, and accessories.')
    home_decor = Category.objects.create(name='Home Decor', slug='home-decor', is_featured=True, description='Elegant items to decorate your living spaces.')
    books = Category.objects.create(name='Books', slug='books', is_featured=False, description='Bestselling literature and educational books.')

    # 5. Create Brands
    print("Creating brands...")
    apple = Brand.objects.create(name='Apple', slug='apple', is_featured=True, description='Think Different.')
    sony = Brand.objects.create(name='Sony', slug='sony', is_featured=True, description='Make Believe.')
    nike = Brand.objects.create(name='Nike', slug='nike', is_featured=True, description='Just Do It.')

    # 6. Create Products
    print("Creating products...")
    
    # iPhone 15 Pro
    iphone = Product.objects.create(
        category=electronics,
        brand=apple,
        name='Apple iPhone 15 Pro Max (256 GB, Natural Titanium)',
        SKU='APL-IP15PM-256',
        description='The ultimate iPhone. Featuring aerospace-grade titanium design, the groundbreaking A17 Pro chip, a customizable Action button, and the most powerful iPhone camera system ever.',
        price=Decimal('159900.00'),
        discount_price=Decimal('148900.00'),
        stock=12,
        is_active=True,
        meta_title='Apple iPhone 15 Pro Max Titanium | PremiumShop AI',
        meta_description='Buy Apple iPhone 15 Pro Max at PremiumShop AI. Top features include A17 Pro chip, Titanium build, and 48MP camera.'
    )
    
    # Sony WH-1000XM5
    sony_headphones = Product.objects.create(
        category=electronics,
        brand=sony,
        name='Sony WH-1000XM5 Wireless Noise Cancelling Headphones',
        SKU='SONY-WH1000XM5-B',
        description='Industry-leading noise cancellation with eight microphones, Auto NC Optimizer, and the Integrated Processor V1. Exceptional audio quality and 30-hour battery life.',
        price=Decimal('34990.00'),
        discount_price=Decimal('29990.00'),
        stock=20,
        is_active=True,
        meta_title='Sony WH-1000XM5 Noise Cancelling Headphones | PremiumShop AI',
        meta_description='Experience pure audio bliss with Sony WH-1000XM5 noise-cancelling headphones.'
    )

    # Nike Air Max
    nike_shoes = Product.objects.create(
        category=fashion,
        brand=nike,
        name='Nike Air Max SC Premium Sneakers',
        SKU='NIKE-AM-SC-001',
        description='With its easy lines, heritage track look, and visible Air cushioning, the Nike Air Max SC is the perfect finish to any outfit. Rich materials add depth while making it durable.',
        price=Decimal('8999.00'),
        stock=15,
        is_active=True,
        meta_title='Nike Air Max SC Premium Sneakers | PremiumShop AI',
        meta_description='Shop original Nike Air Max SC Premium Sneakers with free shipping.'
    )

    # Add size variants for Nike shoes
    ProductVariant.objects.create(product=nike_shoes, name='Size', value='UK 8', stock=5)
    ProductVariant.objects.create(product=nike_shoes, name='Size', value='UK 9', stock=6)
    ProductVariant.objects.create(product=nike_shoes, name='Size', value='UK 10', stock=4)

    # Ceramic Vase (No brand)
    vase = Product.objects.create(
        category=home_decor,
        name='Handcrafted Speckled Ceramic Vase (Beige)',
        SKU='CER-VASE-BEIGE',
        description='Elevate your home with this beautiful handcrafted ceramic vase. Perfect for fresh or dried floral arrangements, its neutral beige speckled glaze matches any modern interior.',
        price=Decimal('1999.00'),
        discount_price=Decimal('1299.00'),
        stock=8,
        is_active=True
    )

    # Rich Dad Poor Dad
    book = Product.objects.create(
        category=books,
        name='Rich Dad Poor Dad: What the Rich Teach Their Kids About Money',
        SKU='BOOK-RDPD-001',
        description='Robert Kiyosaki\'s bestselling personal finance book of all time. Explodes the myth that you need to earn a high income to become rich and explains the difference between working for money and having your money work for you.',
        price=Decimal('599.00'),
        discount_price=Decimal('399.00'),
        stock=50,
        is_active=True
    )

    # 7. Create Coupons
    print("Creating discount coupons...")
    now = timezone.now()
    Coupon.objects.create(
        code='WELCOME100',
        discount_type='FIXED',
        value=Decimal('100.00'),
        min_purchase_amount=Decimal('500.00'),
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=90),
        active=True
    )
    Coupon.objects.create(
        code='PRO500',
        discount_type='FIXED',
        value=Decimal('500.00'),
        min_purchase_amount=Decimal('2000.00'),
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        active=True
    )
    Coupon.objects.create(
        code='SUPER20',
        discount_type='PERCENT',
        value=Decimal('20.00'),
        min_purchase_amount=Decimal('1000.00'),
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        active=True
    )

    # 8. Create Reviews
    print("Writing verified customer reviews...")
    ProductReview.objects.create(
        product=iphone,
        user=customer_user,
        rating=5,
        title='Absolutely stunning phone',
        body='The titanium frame feels incredibly light and premium. The zoom lens is mind-blowing. Price is high, but totally worth it!',
        is_verified_purchase=True,
        status='APPROVED'
    )
    ProductReview.objects.create(
        product=iphone,
        user=reviewer_user,
        rating=4,
        title='Excellent performance, battery could be better',
        body='Super fast processor. High refresh display is beautiful. Battery life is good, but under heavy use it drops faster than expected.',
        is_verified_purchase=True,
        status='APPROVED'
    )

    ProductReview.objects.create(
        product=sony_headphones,
        user=customer_user,
        rating=5,
        title='Best ANC on the market!',
        body='Noise cancellation is unbelievable. Very comfortable to wear for hours, sound quality is crisp and bass is perfectly balanced.',
        is_verified_purchase=True,
        status='APPROVED'
    )

    ProductReview.objects.create(
        product=nike_shoes,
        user=reviewer_user,
        rating=4,
        title='Very comfortable everyday sneakers',
        body='Good cushioning and breathable fit. Runs slightly narrow, so buy one size larger if you have wide feet.',
        is_verified_purchase=True,
        status='APPROVED'
    )

    # 9. Create Notifications
    print("Dispatching initial notification events...")
    Notification.objects.create(
        user=customer_user,
        notification_type='OFFER',
        title='Welcome Offer!',
        message='Welcome to PremiumShop AI! Use coupon WELCOME100 on your first purchase above ₹500 to get ₹100 flat off.',
        link='/products/'
    )
    Notification.objects.create(
        user=customer_user,
        notification_type='ORDER',
        title='Profile Configured',
        message='Your account has been successfully configured. Add addresses and start shopping!',
        link='/accounts/profile/'
    )

    print("Seeding completed successfully!")
    print("\n--- TEST CREDENTIALS ---")
    print("Admin: admin@premiumshop.ai / AdminPass123!")
    print("Customer: customer@premiumshop.ai / CustomerPass123!")
    print("------------------------\n")

if __name__ == '__main__':
    seed()
