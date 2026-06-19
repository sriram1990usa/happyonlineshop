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


import traceback
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def debug_add_category(request):
    try:
        User = get_user_model()
        su = User.objects.filter(is_superuser=True).first()
        if not su:
            return HttpResponse("No superuser found to run diagnostics. Please create a superuser first.")
        
        from django.contrib.admin.sites import site
        from django.test import RequestFactory
        
        rf = RequestFactory()
        req = rf.get('/admin/products/category/add/')
        req.user = su
        
        category_admin = site._registry[Category]
        # Call the add_view directly to simulate rendering the form
        response = category_admin.add_view(req)
        return HttpResponse(f"Success! Admin page loaded successfully with status: {response.status_code}")
        
    except Exception as e:
        tb = traceback.format_exc()
        return HttpResponse(f"<h3>Exception Traceback:</h3><pre>{tb}</pre>", content_type="text/html")
