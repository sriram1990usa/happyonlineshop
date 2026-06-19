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
        
        from django.test import Client
        from django.contrib.admin.sites import site
        import traceback
        
        # Initialize test client and force login
        client = Client()
        client.force_login(su)
        
        results = []
        
        # Sort registered models by app and name
        registry = list(site._registry.items())
        registry.sort(key=lambda item: (item[0]._meta.app_label, item[0]._meta.model_name))
        
        for model, model_admin in registry:
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            add_url = f'/admin/{app_label}/{model_name}/add/'
            
            try:
                # Use client.get to execute the entire request lifecycle (middleware + views)
                response = client.get(add_url, secure=True)
                
                # Extract page title to verify if it redirected to login
                import re
                title_match = re.search(r'<title>(.*?)</title>', response.content.decode('utf-8', errors='ignore'), re.IGNORECASE)
                title = title_match.group(1) if title_match else "No Title"
                
                if response.status_code == 500:
                    results.append(f"""
                    <li style="margin-bottom: 20px;">
                        <strong style="color: #d32f2f;">{app_label}.{model._meta.object_name} (Returned 500)</strong><br>
                        URL: <code>{add_url}</code><br>
                        <div style="background: #ffebee; border: 1px solid #ffcdd2; padding: 10px; color: #b71c1c; max-height: 300px; overflow-y: auto; font-family: monospace;">
                            {response.content.decode('utf-8', errors='ignore')}
                        </div>
                    </li>
                    """)
                else:
                    results.append(f"<li><strong>{app_label}.{model._meta.object_name}</strong>: OK (status {response.status_code}, title: '{title}')</li>")
            except Exception as e:
                tb = traceback.format_exc()
                results.append(f"""
                <li style="margin-bottom: 20px;">
                    <strong style="color: #d32f2f;">{app_label}.{model._meta.object_name} (Raised Exception)</strong><br>
                    URL: <code>{add_url}</code><br>
                    <pre style="background: #ffebee; border: 1px solid #ffcdd2; padding: 10px; color: #b71c1c; overflow-x: auto; border-radius: 4px;">{tb}</pre>
                </li>
                """)
                
        return HttpResponse(f"<h2>Admin Model Diagnostics (with Middleware)</h2><ul>{''.join(results)}</ul>", content_type="text/html")
        
    except Exception as e:
        tb = traceback.format_exc()
        return HttpResponse(f"<h3>Global Diagnostic Exception:</h3><pre>{tb}</pre>", content_type="text/html")


class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        try:
            import traceback
            tb = traceback.format_exc()
            
            from django.contrib.auth import get_user_model
            from notifications.models import Notification
            
            User = get_user_model()
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            
            if user:
                Notification.objects.create(
                    user=user,
                    notification_type='ORDER',
                    title=f"Exception at {request.path}",
                    message=f"Exception: {str(exception)}\n\nTraceback:\n{tb}",
                    link=request.path
                )
        except Exception:
            pass
        return None


def show_debug_errors(request):
    from notifications.models import Notification
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    superusers = [u.email for u in User.objects.filter(is_superuser=True)]
    
    errors = Notification.objects.filter(title__startswith="Exception at")
    
    html = [f"<h2>Admin Superusers in Database</h2><p>{', '.join(superusers)}</p>"]
    html.append("<h2>Logged Server Exceptions</h2>")
    if not errors.exists():
        html.append("<p>No exceptions logged yet.</p>")
    else:
        for err in errors:
            html.append(f"""
            <div style="border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; border-radius: 4px; background: #fdfdfd; font-family: sans-serif;">
                <h3 style="color: #c62828; margin-top: 0;">{err.title}</h3>
                <small style="color: #666;">Logged at: {err.created_at}</small>
                <pre style="background: #f4f4f4; padding: 10px; border: 1px solid #ddd; overflow-x: auto; margin-top: 10px; border-radius: 4px; color: #333;">{err.message}</pre>
            </div>
            """)
            
    return HttpResponse("".join(html), content_type="text/html")
