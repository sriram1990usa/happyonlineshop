from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Avg, Q
from django.utils import timezone

from .models import ProductReview, ReviewImage, DeliveryReview, ReviewVote, ReviewReport, AdminReply
from products.models import Product
from orders.models import Order
from .forms import ProductReviewForm, DeliveryReviewForm

# Permission checks & mixins
class ReviewOwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to ensure only the review author or staff can edit/delete reviews.
    """
    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user or self.request.user.is_staff


# PRODUCT REVIEWS

@method_decorator(login_required, name='dispatch')
class AddProductReviewView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        form = ProductReviewForm(request.POST, request.FILES, user=request.user, product=product)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            
            # Save uploaded photos
            images = request.FILES.getlist('images')
            for img in images:
                ReviewImage.objects.create(product_review=review, image=img)
                
            return JsonResponse({'success': True, 'message': 'Review submitted successfully.'})
        else:
            # Extract first error message
            error_message = next(iter(form.non_field_errors()), 'Invalid review data.')
            if form.errors:
                for field, errors in form.errors.items():
                    if field != '__all__':
                        error_message = f"{field.capitalize()}: {errors[0]}"
                        break
            return JsonResponse({'success': False, 'message': error_message})


class EditProductReviewView(ReviewOwnerRequiredMixin, UpdateView):
    model = ProductReview
    form_class = ProductReviewForm
    template_name = 'reviews/edit_product_review.html'
    context_object_name = 'review'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['product'] = self.object.product
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Review updated successfully.")
        return reverse('products:detail', kwargs={'slug': self.object.product.slug})


class DeleteProductReviewView(ReviewOwnerRequiredMixin, DeleteView):
    model = ProductReview
    template_name = 'reviews/delete_confirm.html'
    context_object_name = 'review'

    def get_success_url(self):
        messages.success(self.request, "Review deleted successfully.")
        return reverse('products:detail', kwargs={'slug': self.object.product.slug})


# DELIVERY REVIEWS

class DeliveryReviewsListView(ListView):
    model = DeliveryReview
    template_name = 'reviews/delivery_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        return DeliveryReview.objects.filter(status='APPROVED').select_related('user', 'order', 'admin_reply__admin').order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        approved_reviews = DeliveryReview.objects.filter(status='APPROVED')
        total_count = approved_reviews.count()
        
        if total_count > 0:
            avg_rating = approved_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            
            # Distribution calculation
            distribution = {}
            for star in range(5, 0, -1):
                count = approved_reviews.filter(rating=star).count()
                percentage = int((count / total_count) * 100)
                distribution[star] = {
                    'count': count,
                    'percentage': percentage
                }
        else:
            avg_rating = 0
            distribution = {star: {'count': 0, 'percentage': 0} for star in range(5, 0, -1)}

        ctx['total_count'] = total_count
        ctx['avg_rating'] = avg_rating
        ctx['distribution'] = distribution
        return ctx


@method_decorator(login_required, name='dispatch')
class AddDeliveryReviewView(View):
    template_name = 'reviews/add_delivery_review.html'

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        if order.status != 'DELIVERED':
            messages.error(request, "Only completed (delivered) orders can have delivery reviews.")
            return redirect('orders:detail', order_number=order.order_number)
            
        if hasattr(order, 'delivery_review'):
            messages.warning(request, "This order already has a delivery review.")
            return redirect('orders:detail', order_number=order.order_number)
            
        form = DeliveryReviewForm(user=request.user, order=order)
        return render(request, self.template_name, {'form': form, 'order': order})

    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        form = DeliveryReviewForm(request.POST, user=request.user, order=order)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.order = order
            review.save()
            messages.success(request, "Delivery review submitted successfully.")
            return redirect('orders:detail', order_number=order.order_number)
        return render(request, self.template_name, {'form': form, 'order': order})


class EditDeliveryReviewView(ReviewOwnerRequiredMixin, UpdateView):
    model = DeliveryReview
    form_class = DeliveryReviewForm
    template_name = 'reviews/edit_delivery_review.html'
    context_object_name = 'review'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['order'] = self.object.order
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Delivery review updated successfully.")
        return reverse('orders:detail', kwargs={'order_number': self.object.order.order_number})


class DeleteDeliveryReviewView(ReviewOwnerRequiredMixin, DeleteView):
    model = DeliveryReview
    template_name = 'reviews/delete_confirm.html'
    context_object_name = 'review'

    def get_success_url(self):
        messages.success(self.request, "Delivery review deleted successfully.")
        return reverse('orders:detail', kwargs={'order_number': self.object.order.order_number})


# CUSTOMER DASHBOARD / MANAGEMENT

class MyReviewsListView(LoginRequiredMixin, ListView):
    template_name = 'reviews/my_reviews.html'
    context_object_name = 'product_reviews'
    paginate_by = 10

    def get_queryset(self):
        return ProductReview.objects.filter(user=self.request.user).select_related('product')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['delivery_reviews'] = DeliveryReview.objects.filter(user=self.request.user).select_related('order')
        return ctx


# VOTING & REPORTING (AJAX Endpoints)

@method_decorator(login_required, name='dispatch')
class VoteReviewView(View):
    def post(self, request, pk):
        review_type = request.POST.get('review_type')  # 'product' or 'delivery'
        vote_type = request.POST.get('vote_type')      # 'HELPFUL' or 'UNHELPFUL'
        
        if vote_type not in ['HELPFUL', 'UNHELPFUL']:
            return JsonResponse({'success': False, 'message': 'Invalid vote type.'})

        if review_type == 'product':
            review = get_object_or_404(ProductReview, pk=pk)
            vote, created = ReviewVote.objects.get_or_create(
                user=request.user,
                product_review=review,
                defaults={'vote_type': vote_type}
            )
        elif review_type == 'delivery':
            review = get_object_or_404(DeliveryReview, pk=pk)
            vote, created = ReviewVote.objects.get_or_create(
                user=request.user,
                delivery_review=review,
                defaults={'vote_type': vote_type}
            )
        else:
            return JsonResponse({'success': False, 'message': 'Invalid review type.'})

        if not created:
            if vote.vote_type == vote_type:
                # If they click the same vote type again, remove the vote
                vote.delete()
                return JsonResponse({'success': True, 'message': 'Vote removed.', 'voted': False})
            else:
                # If they change their vote
                vote.vote_type = vote_type
                vote.save()
                return JsonResponse({'success': True, 'message': 'Vote updated.', 'voted': True, 'vote_type': vote_type})

        return JsonResponse({'success': True, 'message': 'Vote recorded.', 'voted': True, 'vote_type': vote_type})


@method_decorator(login_required, name='dispatch')
class ReportReviewView(View):
    def post(self, request, pk):
        review_type = request.POST.get('review_type')  # 'product' or 'delivery'
        reason = request.POST.get('reason', '').strip()

        if not reason:
            return JsonResponse({'success': False, 'message': 'Reason is required to report.'})

        if review_type == 'product':
            review = get_object_or_404(ProductReview, pk=pk)
            if ReviewReport.objects.filter(user=request.user, product_review=review).exists():
                return JsonResponse({'success': False, 'message': 'You have already reported this review.'})
            ReviewReport.objects.create(user=request.user, product_review=review, reason=reason)
        elif review_type == 'delivery':
            review = get_object_or_404(DeliveryReview, pk=pk)
            if ReviewReport.objects.filter(user=request.user, delivery_review=review).exists():
                return JsonResponse({'success': False, 'message': 'You have already reported this review.'})
            ReviewReport.objects.create(user=request.user, delivery_review=review, reason=reason)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid review type.'})

        return JsonResponse({'success': True, 'message': 'Review has been reported to administrators.'})
