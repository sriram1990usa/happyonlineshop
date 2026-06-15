from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product, Category, Brand
from .serializers import ProductSerializer, CategorySerializer, BrandSerializer


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).prefetch_related('images', 'variants')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category__slug', 'brand__slug', 'price', 'is_low_stock']
    search_fields = ['name', 'description', 'SKU']
    ordering_fields = ['price', 'created_at']


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True).prefetch_related('images', 'variants')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class BrandListAPIView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
