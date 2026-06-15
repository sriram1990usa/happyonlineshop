from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.WishlistView.as_view(), name='wishlist'),
    path('toggle/<int:product_id>/', views.ToggleWishlistView.as_view(), name='toggle'),
]
