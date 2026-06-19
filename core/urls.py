from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('debug-category/', views.debug_add_category, name='debug_add_category'),
]
