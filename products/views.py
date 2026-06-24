from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg
from .models import Product, Category, Brand, ProductVariant


class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).prefetch_related('images')
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        brand = self.request.GET.get('brand')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        sort = self.request.GET.get('sort', '-created_at')

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category:
            cat = Category.objects.filter(slug=category).first()
            if cat:
                qs = qs.filter(Q(category=cat) | Q(category__parent=cat))
        if brand:
            qs = qs.filter(brand__slug=brand)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        sort_map = {
            'price_asc': 'price', 'price_desc': '-price',
            'newest': '-created_at', 'oldest': 'created_at',
        }
        qs = qs.order_by(sort_map.get(sort, '-created_at'))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(parent=None)
        ctx['brands'] = Brand.objects.all()
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_brand'] = self.request.GET.get('brand', '')
        ctx['query'] = self.request.GET.get('q', '')
        ctx['sort'] = self.request.GET.get('sort', '-created_at')
        ctx['min_price'] = self.request.GET.get('min_price', '')
        ctx['max_price'] = self.request.GET.get('max_price', '')
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.get_object()
        ctx['images'] = product.images.all()
        ctx['variants'] = product.variants.all()
        
        # Fetch approved reviews and prefetch related user and replies
        reviews_qs = product.reviews.filter(status='APPROVED').select_related('user', 'admin_reply__admin').prefetch_related('images', 'votes')
        
        # Sorting reviews
        sort = self.request.GET.get('review_sort', 'newest')
        if sort == 'highest':
            reviews_qs = reviews_qs.order_by('-rating', '-created_at')
        elif sort == 'lowest':
            reviews_qs = reviews_qs.order_by('rating', '-created_at')
        elif sort == 'helpful':
            reviews_qs = reviews_qs.annotate(
                helpful_count=Count('votes', filter=Q(votes__vote_type='HELPFUL'))
            ).order_by('-helpful_count', '-created_at')
        else: # default to newest
            reviews_qs = reviews_qs.order_by('-created_at')

        ctx['reviews'] = reviews_qs
        ctx['review_sort'] = sort
        ctx['avg_rating'] = product.average_rating or 0
        
        # Calculate rating distribution breakdown
        total_reviews = reviews_qs.count()
        distribution = {}
        for star in range(5, 0, -1):
            count = reviews_qs.filter(rating=star).count()
            percentage = int((count / total_reviews) * 100) if total_reviews > 0 else 0
            distribution[star] = {
                'count': count,
                'percentage': percentage
            }
        ctx['rating_distribution'] = distribution

        ctx['related_products'] = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(pk=product.pk)[:4]
        
        ctx['in_wishlist'] = False
        ctx['has_purchased'] = False
        ctx['has_reviewed'] = False
        
        if self.request.user.is_authenticated:
            # Check wishlist
            from wishlist.models import Wishlist
            wl = Wishlist.objects.filter(user=self.request.user).first()
            if wl:
                ctx['in_wishlist'] = wl.products.filter(pk=product.pk).exists()
            
            # Check if verified purchaser
            from orders.models import OrderItem
            ctx['has_purchased'] = OrderItem.objects.filter(
                order__user=self.request.user,
                product=product,
                order__status='DELIVERED'
            ).exists()
            
            # Check if user has already reviewed this product to prevent duplicates in frontend
            ctx['has_reviewed'] = product.reviews.filter(user=self.request.user).exists()
            
        return ctx
