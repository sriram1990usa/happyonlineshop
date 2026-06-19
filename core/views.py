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

def debug_admin(request):
    try:
        User = get_user_model()
        su = User.objects.filter(is_superuser=True).first()
        if not su:
            return HttpResponse("No superuser found to run diagnostics. Please create a superuser first.")
        
        from django.contrib.admin.sites import site
        from django.test import RequestFactory
        
        rf = RequestFactory()
        results = []
        
        # Sort registered models by app and name
        registry = list(site._registry.items())
        registry.sort(key=lambda item: (item[0]._meta.app_label, item[0]._meta.model_name))
        
        for model, model_admin in registry:
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            add_url = f'/admin/{app_label}/{model_name}/add/'
            
            try:
                req = rf.get(add_url)
                req.user = su
                response = model_admin.add_view(req)
                results.append(f"<li><strong>{app_label}.{model._meta.object_name}</strong>: OK (status {response.status_code})</li>")
            except Exception as e:
                tb = traceback.format_exc()
                results.append(f"""
                <li style="margin-bottom: 20px;">
                    <strong style="color: #d32f2f;">{app_label}.{model._meta.object_name} (Failed)</strong><br>
                    URL: <code>{add_url}</code><br>
                    <pre style="background: #ffebee; border: 1px solid #ffcdd2; padding: 10px; color: #b71c1c; overflow-x: auto; border-radius: 4px;">{tb}</pre>
                </li>
                """)
                
        return HttpResponse(f"<h2>Admin Model Diagnostics</h2><ul>{''.join(results)}</ul>", content_type="text/html")
        
    except Exception as e:
        tb = traceback.format_exc()
        return HttpResponse(f"<h3>Global Diagnostic Exception:</h3><pre>{tb}</pre>", content_type="text/html")
