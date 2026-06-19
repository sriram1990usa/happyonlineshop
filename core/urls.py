from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('debug-admin/', views.debug_admin, name='debug_admin'),
    path('debug-errors/', views.show_debug_errors, name='show_debug_errors'),
]
