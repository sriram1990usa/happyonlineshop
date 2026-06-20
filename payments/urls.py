from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('webhook/razorpay/', views.RazorpayWebhookView.as_view(), name='razorpay_webhook'),
    path('razorpay/checkout/<str:order_number>/', views.RazorpayCheckoutView.as_view(), name='razorpay_checkout'),
    path('razorpay/verify/', views.RazorpayVerifyView.as_view(), name='razorpay_verify'),
]
