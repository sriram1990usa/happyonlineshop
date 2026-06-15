from rest_framework import serializers
from .models import Cart, CartItem, Coupon
from products.serializers import ProductSerializer, ProductVariantSerializer


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'discount_value', 'min_purchase', 'active']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'variant', 'quantity', 'unit_price', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'coupon', 'subtotal', 'discount', 'shipping_charge', 'total', 'total_items']
