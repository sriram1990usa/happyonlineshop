from products.models import Category
from cart.models import Cart
from wishlist.models import Wishlist

def global_context(request):
    categories = []
    cart_items_count = 0
    wishlist_items_count = 0
    
    try:
        categories = Category.objects.filter(parent=None)[:8]
        
        cart = None
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
            wishlist = Wishlist.objects.filter(user=request.user).first()
            if wishlist:
                wishlist_items_count = wishlist.products.count()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
                
        if cart:
            cart_items_count = cart.total_items
    except Exception:
        # Gracefully handle before database migrations run or on empty db
        pass
        
    return {
        'site_name': 'PremiumShop AI',
        'global_categories': categories,
        'cart_items_count': cart_items_count,
        'wishlist_items_count': wishlist_items_count,
    }
