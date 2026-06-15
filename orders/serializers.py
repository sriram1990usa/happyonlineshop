from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer, ProductVariantSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'shipping_address_snapshot', 
            'payment_method', 'payment_status', 'status', 
            'subtotal', 'discount', 'shipping_charge', 'total', 
            'items', 'created_at'
        ]
