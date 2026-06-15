from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.services import CartService
from cart.models import Coupon
from accounts.models import Address
from decimal import Decimal


class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.orders.all()


class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        order_number = self.kwargs.get('order_number')
        return get_object_or_404(Order, order_number=order_number, user=self.request.user)


class CheckoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        address_id = request.data.get('address_id')
        payment_method = request.data.get('payment_method', 'COD')

        if not address_id:
            return Response({'error': 'address_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        address = get_object_or_404(Address, pk=address_id, user=request.user)
        cart = CartService.get_or_create_cart(request)

        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate totals
        subtotal = cart.subtotal
        coupon = cart.coupon
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

        # Clean cart
        cart.items.all().delete()
        cart.coupon = None
        cart.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
