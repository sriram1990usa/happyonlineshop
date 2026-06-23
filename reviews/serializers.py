from rest_framework import serializers
from .models import ProductReview
from accounts.serializers import UserSerializer

class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'rating', 'title', 'body', 'is_verified_purchase', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'is_verified_purchase', 'status', 'created_at']
