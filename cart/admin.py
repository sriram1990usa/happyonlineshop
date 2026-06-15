from django.contrib import admin
from .models import Cart, CartItem, Coupon

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at', 'total_items', 'subtotal']
    inlines = [CartItemInline]
    search_fields = ['user__email', 'session_key']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'min_purchase_amount', 'active', 'times_used', 'usage_limit']
    list_filter = ['active', 'discount_type']
    search_fields = ['code']
