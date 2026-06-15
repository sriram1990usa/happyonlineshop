from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:product_id>/', views.AddReviewView.as_view(), name='add'),
]
