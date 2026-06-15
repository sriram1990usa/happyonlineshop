from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import CartSerializer
from .services import CartService
from .models import Coupon


class CartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = CartService.get_or_create_cart(request)
        return Response(CartSerializer(cart).data)


class CartAddItemAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))

        cart = CartService.get_or_create_cart(request)
        try:
            CartService.add_item_to_cart(cart, product_id, variant_id, quantity)
            return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CartUpdateItemAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id):
        quantity = int(request.data.get('quantity', 1))
        cart = CartService.get_or_create_cart(request)
        try:
            CartService.update_item_quantity(cart, item_id, quantity)
            return Response(CartSerializer(cart).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CartRemoveItemAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id):
        cart = CartService.get_or_create_cart(request)
        try:
            CartService.remove_item_from_cart(cart, item_id)
            return Response(CartSerializer(cart).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CartApplyCouponAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        cart = CartService.get_or_create_cart(request)
        coupon = Coupon.objects.filter(code=code).first()
        if coupon and coupon.is_valid(cart.subtotal):
            cart.coupon = coupon
            cart.save()
            return Response(CartSerializer(cart).data)
        return Response({'error': 'Invalid or expired coupon'}, status=status.HTTP_400_BAD_REQUEST)
