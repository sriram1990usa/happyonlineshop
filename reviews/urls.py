from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Product Reviews
    path('add/<int:product_id>/', views.AddProductReviewView.as_view(), name='add'),
    path('product/edit/<int:pk>/', views.EditProductReviewView.as_view(), name='edit_product_review'),
    path('product/delete/<int:pk>/', views.DeleteProductReviewView.as_view(), name='delete_product_review'),
    
    # Delivery Reviews
    path('delivery/', views.DeliveryReviewsListView.as_view(), name='delivery_reviews_list'),
    path('delivery/add/<str:order_number>/', views.AddDeliveryReviewView.as_view(), name='add_delivery_review'),
    path('delivery/edit/<int:pk>/', views.EditDeliveryReviewView.as_view(), name='edit_delivery_review'),
    path('delivery/delete/<int:pk>/', views.DeleteDeliveryReviewView.as_view(), name='delete_delivery_review'),
    
    # Dashboard & General
    path('my-reviews/', views.MyReviewsListView.as_view(), name='my_reviews'),
    path('vote/<int:pk>/', views.VoteReviewView.as_view(), name='vote_review'),
    path('report/<int:pk>/', views.ReportReviewView.as_view(), name='report_review'),
]
