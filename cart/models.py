from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant
from decimal import Decimal
from django.utils import timezone

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart of User: {self.user.email}"
        return f"Cart of Session: {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def unit_price(self):
        if self.variant and self.variant.price_override:
            return self.variant.price_override
        return self.product.current_price

    @property
    def total_price(self):
        return Decimal(self.unit_price) * self.quantity

    def __str__(self):
        variant_desc = f" ({self.variant})" if self.variant else ""
        return f"{self.quantity} x {self.product.name}{variant_desc}"

class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('PERCENT', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
        ('FREE_SHIPPING', 'Free Shipping'),
    )
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPES, default='PERCENT')
    value = models.DecimalField(max_digits=12, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(default=100)
    times_used = models.IntegerField(default=0)

    def is_valid(self, cart_subtotal=Decimal('0.00')):
        now = timezone.now()
        if not self.active:
            return False
        if not (self.start_date <= now <= self.end_date):
            return False
        if self.times_used >= self.usage_limit:
            return False
        if cart_subtotal < self.min_purchase_amount:
            return False
        return True

    def calculate_discount(self, subtotal):
        if self.discount_type == 'PERCENT':
            return (subtotal * self.value) / Decimal('100.00')
        elif self.discount_type == 'FIXED':
            return min(self.value, subtotal)
        elif self.discount_type == 'FREE_SHIPPING':
            return Decimal('0.00')
        return Decimal('0.00')

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()} ({self.value})"
