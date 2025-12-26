from .models import Cart, Category

def cart_context(request):
    """Context processor to add cart information to all templates"""
    context = {
        'cart_total_items': 0,
        'cart_total_price': 0,
    }
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            context['cart_total_items'] = cart.total_items
            context['cart_total_price'] = cart.total_price
        except Cart.DoesNotExist:
            # Cart doesn't exist yet, will be created when needed
            pass
        except Exception:
            # Handle any other errors gracefully
            pass
    
    return context

def categories_context(request):
    """Context processor to add categories to all templates"""
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}

