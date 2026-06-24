from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from orders.models import Order, OrderItem
from accounts.models import User
from notifications.models import Notification


def is_staff(user):
    return user.is_staff or user.is_superuser


@method_decorator([login_required, user_passes_test(is_staff)], name='dispatch')
class DashboardHomeView(View):
    template_name = 'dashboard/home.html'

    def get(self, request):
        today = timezone.now().date()
        last_30 = today - timedelta(days=30)

        total_revenue = Order.objects.filter(payment_status='PAID').aggregate(total=Sum('total'))['total'] or 0
        total_orders = Order.objects.count()
        total_customers = User.objects.filter(is_staff=False).count()
        total_products = Product.objects.filter(is_active=True).count()

        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        low_stock = Product.objects.filter(is_active=True, stock__lt=10).order_by('stock')[:8]

        # Review stats for dashboard
        from reviews.models import ProductReview, DeliveryReview, ReviewReport
        pending_reviews_count = ProductReview.objects.filter(status='PENDING').count() + DeliveryReview.objects.filter(status='PENDING').count()
        reported_reviews_count = ReviewReport.objects.filter(status='PENDING').count()
        avg_delivery_rating = DeliveryReview.objects.filter(status='APPROVED').aggregate(avg=Avg('rating'))['avg'] or 0

        # Monthly revenue chart data (last 7 days)
        daily_revenue = []
        daily_labels = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            rev = Order.objects.filter(
                created_at__date=day, payment_status='PAID'
            ).aggregate(t=Sum('total'))['t'] or 0
            daily_revenue.append(float(rev))
            daily_labels.append(day.strftime('%d %b'))

        context = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'total_customers': total_customers,
            'total_products': total_products,
            'recent_orders': recent_orders,
            'low_stock': low_stock,
            'daily_revenue': daily_revenue,
            'daily_labels': daily_labels,
            # reviews stats
            'pending_reviews_count': pending_reviews_count,
            'reported_reviews_count': reported_reviews_count,
            'avg_delivery_rating': avg_delivery_rating,
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, user_passes_test(is_staff)], name='dispatch')
class DashboardOrdersView(View):
    template_name = 'dashboard/orders.html'

    def get(self, request):
        orders = Order.objects.select_related('user').order_by('-created_at')
        status_filter = request.GET.get('status', '')
        if status_filter:
            orders = orders.filter(status=status_filter)
        return render(request, self.template_name, {'orders': orders, 'status_filter': status_filter})

    def post(self, request):
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.objects.get(pk=order_id)
        
        if order.status in ['DELIVERED', 'CANCELLED'] and new_status != order.status:
            from django.contrib import messages
            messages.error(request, f"Status of a finalized order ({order.get_status_display()}) cannot be modified.")
            return redirect('dashboard:orders')
        
        if new_status == 'SHIPPED':
            order.courier_name = request.POST.get('courier_name', '').strip() or None
            order.tracking_number = request.POST.get('tracking_number', '').strip() or None
            order.tracking_url = request.POST.get('tracking_url', '').strip() or None
            if not order.shipped_at:
                order.shipped_at = timezone.now()
        elif new_status == 'DELIVERED':
            order.delivery_proof_notes = request.POST.get('delivery_proof_notes', '').strip() or None
            if 'delivery_proof_image' in request.FILES:
                order.delivery_proof_image = request.FILES['delivery_proof_image']
            if not order.delivered_at:
                order.delivered_at = timezone.now()

        order.status = new_status
        order.save()
        return redirect('dashboard:orders')


@method_decorator([login_required, user_passes_test(is_staff)], name='dispatch')
class DashboardProductsView(View):
    template_name = 'dashboard/products.html'

    def get(self, request):
        products = Product.objects.all().select_related('category', 'brand')
        return render(request, self.template_name, {'products': products})


@method_decorator([login_required, user_passes_test(is_staff)], name='dispatch')
class DashboardReviewsView(View):
    template_name = 'dashboard/reviews.html'

    def get(self, request):
        tab = request.GET.get('tab', 'reports')
        from reviews.models import ProductReview, DeliveryReview, ReviewReport

        # Get reports
        reports = ReviewReport.objects.select_related(
            'user', 'product_review__product', 'product_review__user',
            'delivery_review__order', 'delivery_review__user'
        ).order_by('-created_at')

        # Get product reviews
        product_reviews = ProductReview.objects.select_related(
            'product', 'user', 'admin_reply__admin'
        ).order_by('-created_at')

        # Get delivery reviews
        delivery_reviews = DeliveryReview.objects.select_related(
            'order', 'user', 'admin_reply__admin'
        ).order_by('-created_at')

        # Filter by status if specified
        status_filter = request.GET.get('status', '')
        if status_filter:
            if tab == 'product':
                product_reviews = product_reviews.filter(status=status_filter)
            elif tab == 'delivery':
                delivery_reviews = delivery_reviews.filter(status=status_filter)
            elif tab == 'reports':
                reports = reports.filter(status=status_filter)

        context = {
            'tab': tab,
            'reports': reports,
            'product_reviews': product_reviews,
            'delivery_reviews': delivery_reviews,
            'status_filter': status_filter,
            'pending_reports_count': ReviewReport.objects.filter(status='PENDING').count(),
            'pending_product_count': ProductReview.objects.filter(status='PENDING').count(),
            'pending_delivery_count': DeliveryReview.objects.filter(status='PENDING').count(),
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, user_passes_test(is_staff)], name='dispatch')
class DashboardReviewsActionView(View):
    def post(self, request):
        from django.shortcuts import get_object_or_404
        from django.urls import reverse
        from django.contrib import messages
        from reviews.models import ProductReview, DeliveryReview, ReviewReport, AdminReply

        action = request.POST.get('action')
        pk = request.POST.get('id')

        if action == 'approve_product':
            review = get_object_or_404(ProductReview, pk=pk)
            review.status = 'APPROVED'
            review.save()
            messages.success(request, "Product review approved successfully.")
        elif action == 'reject_product':
            review = get_object_or_404(ProductReview, pk=pk)
            review.status = 'REJECTED'
            review.save()
            messages.success(request, "Product review rejected.")
        elif action == 'delete_product':
            review = get_object_or_404(ProductReview, pk=pk)
            review.delete()
            messages.success(request, "Product review deleted successfully.")
        elif action == 'approve_delivery':
            review = get_object_or_404(DeliveryReview, pk=pk)
            review.status = 'APPROVED'
            review.save()
            messages.success(request, "Delivery review approved successfully.")
        elif action == 'reject_delivery':
            review = get_object_or_404(DeliveryReview, pk=pk)
            review.status = 'REJECTED'
            review.save()
            messages.success(request, "Delivery review rejected.")
        elif action == 'delete_delivery':
            review = get_object_or_404(DeliveryReview, pk=pk)
            review.delete()
            messages.success(request, "Delivery review deleted successfully.")
        elif action == 'resolve_report':
            report = get_object_or_404(ReviewReport, pk=pk)
            report.status = 'ACTIONED'
            report.save()
            messages.success(request, "Review report marked as Actioned.")
        elif action == 'dismiss_report':
            report = get_object_or_404(ReviewReport, pk=pk)
            report.status = 'DISMISSED'
            report.save()
            messages.success(request, "Review report dismissed.")
        elif action == 'reply_product':
            review = get_object_or_404(ProductReview, pk=pk)
            body = request.POST.get('body', '').strip()
            if body:
                reply, created = AdminReply.objects.get_or_create(
                    product_review=review,
                    defaults={'admin': request.user, 'body': body}
                )
                if not created:
                    reply.body = body
                    reply.admin = request.user
                    reply.save()
                messages.success(request, "Admin reply added to product review.")
            else:
                messages.error(request, "Reply body cannot be empty.")
        elif action == 'reply_delivery':
            review = get_object_or_404(DeliveryReview, pk=pk)
            body = request.POST.get('body', '').strip()
            if body:
                reply, created = AdminReply.objects.get_or_create(
                    delivery_review=review,
                    defaults={'admin': request.user, 'body': body}
                )
                if not created:
                    reply.body = body
                    reply.admin = request.user
                    reply.save()
                messages.success(request, "Admin reply added to delivery review.")
            else:
                messages.error(request, "Reply body cannot be empty.")

        tab = request.POST.get('tab', 'reports')
        return redirect(f"{reverse('dashboard:reviews')}?tab={tab}")
