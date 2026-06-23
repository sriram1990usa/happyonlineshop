from django import forms
from .models import ProductReview, DeliveryReview
from orders.models import OrderItem, Order

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class ProductReviewForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'class': 'hidden', 'id': 'review-images-input'}),
        required=False,
        label="Upload Photos"
    )

    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'body']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'id': 'review-rating-input'}),
            'title': forms.TextInput(attrs={'placeholder': 'Summarize your experience...', 'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-brand-500 focus:outline-none text-sm'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What did you like or dislike? How does it fit?', 'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-brand-500 focus:outline-none text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not self.user or not self.product:
            raise forms.ValidationError("User and product contexts are required.")

        # Check for duplicate reviews
        # If updating (instance exists), we bypass the duplicate check
        if not self.instance.pk:
            if ProductReview.objects.filter(user=self.user, product=self.product).exists():
                raise forms.ValidationError("You have already reviewed this product.")

        # Check if the user is a verified purchaser
        # The user has successfully purchased if there is a completed/paid OrderItem
        has_purchased = OrderItem.objects.filter(
            order__user=self.user,
            product=self.product
        ).filter(
            models.Q(order__status='DELIVERED') | models.Q(order__payment_status='PAID')
        ).exists() if hasattr(self, 'models') else True # we import models inside clean just in case or use standard django Q
        
        # Standard Q check
        from django.db.models import Q
        has_purchased = OrderItem.objects.filter(
            order__user=self.user,
            product=self.product
        ).filter(
            Q(order__status='DELIVERED') | Q(order__payment_status='PAID')
        ).exists()

        if not has_purchased:
            raise forms.ValidationError("Only verified purchasers of this product can submit a review.")

        return cleaned_data


class DeliveryReviewForm(forms.ModelForm):
    class Meta:
        model = DeliveryReview
        fields = ['rating', 'body']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about your delivery experience...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not self.user or not self.order:
            raise forms.ValidationError("User and order contexts are required.")

        # Validate order owner
        if self.order.user != self.user:
            raise forms.ValidationError("You can only review your own orders.")

        # Validate order completed
        if self.order.status != 'DELIVERED':
            raise forms.ValidationError("Only completed (delivered) orders can have delivery reviews.")

        # Prevent duplicates
        if not self.instance.pk:
            if DeliveryReview.objects.filter(order=self.order).exists():
                raise forms.ValidationError("This order has already been reviewed for delivery.")

        return cleaned_data
