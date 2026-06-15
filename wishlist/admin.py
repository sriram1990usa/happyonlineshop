from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__email']
