from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/address/', views.CheckoutAddressView.as_view(), name='checkout_address'),
    path('checkout/payment/', views.CheckoutPaymentView.as_view(), name='checkout_payment'),
    path('confirmation/<str:order_number>/', views.OrderConfirmationView.as_view(), name='confirmation'),
    path('my-orders/', views.OrderListView.as_view(), name='list'),
    path('my-orders/<str:order_number>/', views.OrderDetailView.as_view(), name='detail'),
    path('my-orders/<str:order_number>/invoice/', views.OrderInvoiceDownloadView.as_view(), name='order_invoice'),
]
