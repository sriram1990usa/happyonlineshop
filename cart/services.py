from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Coupon
from products.models import Product, ProductVariant
from decimal import Decimal
from django.utils import timezone

class CartService:
    @staticmethod
    def get_or_create_cart(request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            return cart
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            return cart

    @staticmethod
    def add_item_to_cart(cart, product_id, variant_id=None, quantity=1):
        product = Product.objects.get(id=product_id)
        variant = None
        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id)
            
        # Check stock limits
        available_stock = variant.stock if variant else product.stock
        
        # Get or create item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': 0}
        )
        
        new_quantity = cart_item.quantity + int(quantity)
        if new_quantity > available_stock:
            # Clamp to maximum available stock
            cart_item.quantity = available_stock
        else:
            cart_item.quantity = new_quantity
            
        if cart_item.quantity > 0:
            cart_item.save()
        else:
            cart_item.delete()
            
        return cart_item

    @staticmethod
    def update_item_quantity(cart, item_id, quantity):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            quantity = int(quantity)
            if quantity <= 0:
                cart_item.delete()
                return None
            
            available_stock = cart_item.variant.stock if cart_item.variant else cart_item.product.stock
            if quantity > available_stock:
                cart_item.quantity = available_stock
            else:
                cart_item.quantity = quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            return None

    @staticmethod
    def remove_item_from_cart(cart, item_id):
        CartItem.objects.filter(id=item_id, cart=cart).delete()

    @staticmethod
    def merge_session_cart_to_user(request, user):
        session_key = request.session.session_key
        if not session_key:
            return
            
        session_cart = Cart.objects.filter(session_key=session_key).first()
        if not session_cart:
            return
            
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        # Merge items
        for item in session_cart.items.all():
            user_item, item_created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                variant=item.variant,
                defaults={'quantity': 0}
            )
            
            available_stock = item.variant.stock if item.variant else item.product.stock
            merged_quantity = user_item.quantity + item.quantity
            user_item.quantity = min(merged_quantity, available_stock)
            user_item.save()
            
        # Delete session cart
        session_cart.delete()
