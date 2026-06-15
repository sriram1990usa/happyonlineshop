from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import View
from django.contrib import messages
from .models import Cart, CartItem
from .services import CartService
from cart.models import Coupon
import json


class CartDetailView(View):
    template_name = 'cart/detail.html'

    def get(self, request):
        cart = CartService.get_or_create_cart(request)
        return render(request, self.template_name, {'cart': cart})


class AddToCartView(View):
    def post(self, request):
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))

        cart = CartService.get_or_create_cart(request)
        try:
            item = CartService.add_item_to_cart(cart, product_id, variant_id, quantity)
            return JsonResponse({'success': True, 'cart_count': cart.total_items, 'message': 'Added to cart'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


class UpdateCartItemView(View):
    def post(self, request, item_id):
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        quantity = data.get('quantity', 1)
        cart = CartService.get_or_create_cart(request)
        CartService.update_item_quantity(cart, item_id, quantity)
        return JsonResponse({'success': True, 'cart_count': cart.total_items, 'subtotal': str(cart.subtotal)})


class RemoveCartItemView(View):
    def post(self, request, item_id):
        cart = CartService.get_or_create_cart(request)
        CartService.remove_item_from_cart(cart, item_id)
        return JsonResponse({'success': True, 'cart_count': cart.total_items, 'subtotal': str(cart.subtotal)})


class ApplyCouponView(View):
    def post(self, request):
        code = request.POST.get('code', '').strip().upper()
        cart = CartService.get_or_create_cart(request)
        coupon = Coupon.objects.filter(code=code).first()
        if coupon and coupon.is_valid(cart.subtotal):
            request.session['coupon_id'] = coupon.id
            discount = coupon.calculate_discount(cart.subtotal)
            messages.success(request, f'Coupon "{code}" applied! You save ₹{discount:.2f}')
        else:
            request.session.pop('coupon_id', None)
            messages.error(request, f'Coupon "{code}" is invalid or expired.')
        return redirect('cart:detail')
