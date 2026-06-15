from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='detail'),
    path('add/', views.AddToCartView.as_view(), name='add'),
    path('update/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update'),
    path('remove/<int:item_id>/', views.RemoveCartItemView.as_view(), name='remove'),
    path('coupon/apply/', views.ApplyCouponView.as_view(), name='apply_coupon'),
]
