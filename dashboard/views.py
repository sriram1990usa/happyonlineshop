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
