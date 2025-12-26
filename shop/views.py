"""
This module contains views for an e-commerce site built with Django. It provides functionality for 
displaying products, managing user interactions such as adding items to the cart, handling wishlists, 
and processing orders. Below is a summary of the views and their functionality:
Views:
------
1. home(request):
    - Displays the homepage with featured products, categories, and products on sale.
2. product_list(request):
    - Displays a list of products with filtering, searching, sorting, and pagination options.
3. product_detail(request, slug):
    - Displays detailed information about a specific product, including related products, reviews, 
      and wishlist status.
4. add_to_cart(request, product_id):
    - Allows authenticated users to add products to their shopping cart.
5. cart_view(request):
    - Displays the user's shopping cart and allows updating quantities or removing items.
6. checkout(request):
    - Handles the checkout process, including creating an order and clearing the cart.
7. wishlist_view(request):
    - Displays the user's wishlist and allows adding or removing products via AJAX.
8. order_history(request):
    - Displays the user's order history.
9. order_detail(request, order_id):
    - Displays detailed information about a specific order.
Dependencies:
-------------
- Django modules:
    - django.shortcuts (render, get_object_or_404, redirect)
    - django.contrib.auth.decorators (login_required)
    - django.contrib (messages)
    - django.db.models (Q, Avg)
    - django.core.paginator (Paginator)
    - django.http (JsonResponse)
- Local imports:
    - .models (Product, Category, Wishlist, Cart, CartItem, Order, OrderItem, etc.)
    - .forms (CheckoutForm, ReviewForm)
Required Installations:
-----------------------
Ensure the following modules are installed:
1. Django: `pip install django`
2. Any additional dependencies for your project (e.g., Pillow for image handling).
Notes:
------
- Ensure that the `forms.py` file contains the `CheckoutForm` and `ReviewForm` classes.
- Templates such as `home.html`, `shop/product_list.html`, `shop/product_detail.html`, etc., 
  must exist in the appropriate directories.
"""

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import *
from .forms import CheckoutForm, ReviewForm
import json
from django.http import JsonResponse

def home(request):
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True)
    
    # Get products on sale
    on_sale_products = Product.objects.filter(
        is_active=True, 
        discount_price__isnull=False
    )[:4]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'on_sale_products': on_sale_products,
    }
    return render(request, 'home.html', context)

def product_list(request):
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'newest')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    products = Product.objects.filter(is_active=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_slug': category_slug,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Calculate average rating
    avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user, 
            product=product
        ).exists()
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('product_detail', slug=slug)
    else:
        form = ReviewForm()
    
    context = {
        'product': product,
        'related_products': related_products,
        'avg_rating': avg_rating,
        'form': form,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'shop/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Check stock availability
        if not product.is_in_stock():
            messages.error(request, f'Sorry, {product.name} is out of stock!')
            return redirect('product_detail', slug=product.slug)
        
        # Get or create user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if product already in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                messages.error(request, f'Only {product.stock} items available in stock!')
                return redirect('product_detail', slug=product.slug)
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            if quantity > product.stock:
                messages.error(request, f'Only {product.stock} items available in stock!')
                cart_item.delete()
                return redirect('product_detail', slug=product.slug)
        
        messages.success(request, f'{product.name} added to cart!')
    
    return redirect('cart')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle quantity updates
        for item in cart.items.all():
            new_quantity = request.POST.get(f'quantity_{item.id}')
            if new_quantity and new_quantity.isdigit():
                new_quantity = int(new_quantity)
                if new_quantity <= 0:
                    item.delete()
                elif new_quantity > item.product.stock:
                    messages.error(request, f'Only {item.product.stock} items available for {item.product.name}!')
                else:
                    item.quantity = new_quantity
                    item.save()
        
        # Handle remove items
        remove_item = request.POST.get('remove_item')
        if remove_item:
            try:
                item = CartItem.objects.get(id=remove_item, cart=cart)
                item.delete()
                messages.success(request, 'Item removed from cart!')
            except CartItem.DoesNotExist:
                pass
        
        if not remove_item:
            messages.success(request, 'Cart updated!')
        return redirect('cart')
    
    context = {
        'cart': cart,
    }
    return render(request, 'shop/cart.html', context)

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if cart.items.count() == 0:
        messages.warning(request, 'Your cart is empty!')
        return redirect('product_list')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.total_price
            order.final_amount = cart.total_price  # Calculate with discounts later
            
            # Build shipping and billing addresses from form data
            address_parts = [
                form.cleaned_data.get('address', ''),
                form.cleaned_data.get('city', ''),
                form.cleaned_data.get('state', ''),
                form.cleaned_data.get('postal_code', ''),
                form.cleaned_data.get('country', '')
            ]
            shipping_address = ', '.join(filter(None, address_parts))
            order.shipping_address = shipping_address
            order.billing_address = shipping_address  # Default to same as shipping
            
            # Validate cart items are still in stock
            for cart_item in cart.items.all():
                if cart_item.quantity > cart_item.product.stock:
                    messages.error(request, f'Sorry, {cart_item.product.name} only has {cart_item.product.stock} items in stock!')
                    return redirect('cart')
            
            order.save()
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.get_final_price(),
                    total_price=cart_item.total_price
                )
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, f'Order #{order.order_id} placed successfully!')
            return redirect('order_detail', order_id=order.order_id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'email': request.user.email or '',
                'first_name': request.user.first_name or '',
                'last_name': request.user.last_name or '',
            }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        
        if product_id and action:
            product = get_object_or_404(Product, id=product_id)
            
            if action == 'add':
                Wishlist.objects.get_or_create(user=request.user, product=product)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'added'})
                messages.success(request, f'{product.name} added to wishlist!')
            elif action == 'remove':
                Wishlist.objects.filter(user=request.user, product=product).delete()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'removed'})
                messages.success(request, f'{product.name} removed from wishlist!')
        
        return redirect('wishlist')
    
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})

@login_required
def update_cart_item(request, item_id):
    """AJAX endpoint to update cart item quantity"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity <= 0:
                cart_item.delete()
                return JsonResponse({'success': True, 'message': 'Item removed'})
            
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False, 
                    'message': f'Only {cart_item.product.stock} items available!'
                })
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'item_total': str(cart_item.total_price),
                'cart_total': str(cart_item.cart.total_price),
                'cart_items': cart_item.cart.total_items
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def wishlist_toggle(request):
    """AJAX endpoint to toggle wishlist items"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        
        if product_id and action:
            try:
                product = Product.objects.get(id=product_id)
                
                if action == 'add':
                    Wishlist.objects.get_or_create(user=request.user, product=product)
                    return JsonResponse({'status': 'added'})
                elif action == 'remove':
                    Wishlist.objects.filter(user=request.user, product=product).delete()
                    return JsonResponse({'status': 'removed'})
            except Product.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Product not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})