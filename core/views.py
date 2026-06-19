from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product, Category, Brand


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['featured_categories'] = Category.objects.filter(is_featured=True, parent=None)[:8]
        ctx['trending_products'] = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
        ctx['best_sellers'] = Product.objects.filter(is_active=True).order_by('price')[:4]
        ctx['new_arrivals'] = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
        ctx['featured_brands'] = Brand.objects.filter(is_featured=True)[:6]
        ctx['flash_sale_products'] = Product.objects.filter(
            is_active=True, discount_price__isnull=False
        ).order_by('-created_at')[:6]
        return ctx


def handler404(request, exception):
    return render(request, 'core/404.html', status=404)
