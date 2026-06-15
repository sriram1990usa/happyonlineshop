from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from django.contrib import messages
from reviews.models import Review
from products.models import Product
from .forms import ReviewForm


@method_decorator(login_required, name='dispatch')
class AddReviewView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        existing = Review.objects.filter(user=request.user, product=product).first()
        if existing:
            return JsonResponse({'success': False, 'message': 'You have already reviewed this product.'})
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return JsonResponse({'success': True, 'message': 'Review submitted for approval.'})
        return JsonResponse({'success': False, 'errors': form.errors})
