from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('orders/', views.DashboardOrdersView.as_view(), name='orders'),
    path('products/', views.DashboardProductsView.as_view(), name='products'),
]
