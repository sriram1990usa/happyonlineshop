from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from .models import Wishlist
from products.models import Product


@method_decorator(login_required, name='dispatch')
class WishlistView(View):
    template_name = 'wishlist/wishlist.html'

    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        return render(request, self.template_name, {'wishlist': wishlist})


@method_decorator(login_required, name='dispatch')
class ToggleWishlistView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        if wishlist.products.filter(pk=product_id).exists():
            wishlist.products.remove(product)
            return JsonResponse({'added': False, 'message': 'Removed from wishlist'})
        else:
            wishlist.products.add(product)
            return JsonResponse({'added': True, 'message': 'Added to wishlist'})
