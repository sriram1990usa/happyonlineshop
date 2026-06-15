from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Review
from .serializers import ReviewSerializer
from products.models import Product


class ProductReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        return Review.objects.filter(product__slug=product_slug, is_approved=True)

    def perform_create(self, serializer):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        
        # Check if already reviewed
        if Review.objects.filter(user=self.request.user, product=product).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You have already reviewed this product.")

        serializer.save(user=self.request.user, product=product)
        
        # In a real system, review goes to approval. For ease in API we could default is_approved to True or handle it.
        # Let's auto-approve for API demo purposes or respect model default. Since model default is False, let's keep it.
