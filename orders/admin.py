from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_method', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'shipping_address_snapshot', 'courier_name', 'tracking_number']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'shipped_at', 'delivered_at']

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_status', 'subtotal', 'discount', 'shipping_charge', 'total', 'coupon', 'razorpay_order_id')
        }),
        ('Shipping & Address', {
            'fields': ('shipping_address_snapshot',)
        }),
        ('Tracking & Delivery', {
            'fields': ('courier_name', 'tracking_number', 'tracking_url', 'shipped_at', 'delivered_at', 'delivery_proof_image', 'delivery_proof_notes')
        }),
    )
