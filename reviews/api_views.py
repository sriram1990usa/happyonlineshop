from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ProductReview
from .serializers import ProductReviewSerializer
from products.models import Product

class ProductReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        return ProductReview.objects.filter(product__slug=product_slug, status='APPROVED')

    def perform_create(self, serializer):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        
        # Check if already reviewed
        if ProductReview.objects.filter(user=self.request.user, product=product).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You have already reviewed this product.")

        serializer.save(user=self.request.user, product=product)
