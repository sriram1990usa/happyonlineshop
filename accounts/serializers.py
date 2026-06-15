from rest_framework import serializers
from .models import User, Profile, Address


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'phone_number', 'avatar']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'recipient_name', 'phone_number', 'street_address', 'city', 'state', 'postal_code', 'country', 'address_type', 'is_default']
        read_only_fields = ['id', 'user']
