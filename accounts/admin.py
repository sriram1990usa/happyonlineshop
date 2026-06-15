from django.contrib import admin
from .models import User, Profile, Address

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'wallet_balance', 'loyalty_points']
    search_fields = ['user__email', 'phone_number']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipient_name', 'city', 'state', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default', 'state']
    search_fields = ['user__email', 'recipient_name', 'city']
