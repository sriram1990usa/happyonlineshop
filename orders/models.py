from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant
from cart.models import Coupon
from decimal import Decimal
import uuid

class Order(models.Model):
    ORDER_STATUS = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned'),
        ('REFUNDED', 'Refunded'),
    )
    PAYMENT_METHODS = (
        ('COD', 'Cash On Delivery'),
        ('STRIPE', 'Stripe'),
        ('RAZORPAY', 'Razorpay'),
    )
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING', db_index=True)
    
    # Store address as snapshot text so if address changes, order details remain accurate
    shipping_address_snapshot = models.TextField()
    
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS, default='COD')
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='PENDING')
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_charge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = 'ORD-' + str(uuid.uuid4().hex[:12]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order: {self.order_number} ({self.get_status_display()})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)  # Purchase price snapshot

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'}"
