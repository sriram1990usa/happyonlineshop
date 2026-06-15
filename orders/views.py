from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Order, OrderItem
from cart.services import CartService
from cart.models import Cart, Coupon
from accounts.models import Address
from payments.models import Transaction
from decimal import Decimal
import json


@method_decorator(login_required, name='dispatch')
class CheckoutAddressView(View):
    template_name = 'orders/checkout_address.html'

    def get(self, request):
        addresses = request.user.addresses.all()
        cart = CartService.get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('cart:detail')
        return render(request, self.template_name, {'addresses': addresses, 'cart': cart})

    def post(self, request):
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        request.session['checkout_address_id'] = address_id
        return redirect('orders:checkout_payment')


@method_decorator(login_required, name='dispatch')
class CheckoutPaymentView(View):
    template_name = 'orders/checkout_payment.html'

    def get(self, request):
        address_id = request.session.get('checkout_address_id')
        if not address_id:
            return redirect('orders:checkout_address')
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        cart = CartService.get_or_create_cart(request)
        coupon = None
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()

        subtotal = cart.subtotal
        discount = coupon.calculate_discount(subtotal) if coupon and coupon.is_valid(subtotal) else Decimal('0.00')
        shipping = Decimal('49.00') if subtotal < 500 else Decimal('0.00')
        if coupon and coupon.discount_type == 'FREE_SHIPPING':
            shipping = Decimal('0.00')
        total = subtotal - discount + shipping

        return render(request, self.template_name, {
            'address': address, 'cart': cart, 'coupon': coupon,
            'subtotal': subtotal, 'discount': discount,
            'shipping': shipping, 'total': total,
        })

    def post(self, request):
        payment_method = request.POST.get('payment_method', 'COD')
        address_id = request.session.get('checkout_address_id')
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        cart = CartService.get_or_create_cart(request)

        coupon = None
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()

        subtotal = cart.subtotal
        discount = coupon.calculate_discount(subtotal) if coupon and coupon.is_valid(subtotal) else Decimal('0.00')
        shipping = Decimal('49.00') if subtotal < 500 else Decimal('0.00')
        if coupon and coupon.discount_type == 'FREE_SHIPPING':
            shipping = Decimal('0.00')
        total = subtotal - discount + shipping

        address_snapshot = f"{address.recipient_name}\n{address.phone_number}\n{address.street_address}\n{address.city}, {address.state} - {address.postal_code}\n{address.country}"

        order = Order.objects.create(
            user=request.user,
            shipping_address_snapshot=address_snapshot,
            payment_method=payment_method,
            payment_status='PAID' if payment_method != 'COD' else 'PENDING',
            subtotal=subtotal,
            discount=discount,
            shipping_charge=shipping,
            total=total,
            coupon=coupon,
            status='CONFIRMED' if payment_method == 'COD' else 'PENDING',
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=item.unit_price,
            )
            # Decrease product stock
            if item.variant:
                item.variant.stock = max(0, item.variant.stock - item.quantity)
                item.variant.save()
            else:
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save()

        if coupon:
            coupon.times_used += 1
            coupon.save()

        cart.items.all().delete()
        request.session.pop('coupon_id', None)
        request.session.pop('checkout_address_id', None)

        messages.success(request, f'Order #{order.order_number} placed successfully!')
        return redirect('orders:confirmation', order_number=order.order_number)


@method_decorator(login_required, name='dispatch')
class OrderConfirmationView(View):
    template_name = 'orders/confirmation.html'

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        return render(request, self.template_name, {'order': order})


@method_decorator(login_required, name='dispatch')
class OrderListView(View):
    template_name = 'orders/list.html'

    def get(self, request):
        orders = request.user.orders.all().order_by('-created_at')
        return render(request, self.template_name, {'orders': orders})


@method_decorator(login_required, name='dispatch')
class OrderDetailView(View):
    template_name = 'orders/detail.html'

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        return render(request, self.template_name, {'order': order})
