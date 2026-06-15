from rest_framework import serializers
from .models import Review
from accounts.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'title', 'body', 'is_approved', 'created_at']
        read_only_fields = ['id', 'user', 'is_approved', 'created_at']
