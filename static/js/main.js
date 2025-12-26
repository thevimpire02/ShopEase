$(document).ready(function() {
    // Product quantity controls
    $('.btn-minus').click(function() {
        var input = $(this).siblings('input');
        var value = parseInt(input.val());
        if (value > 1) {
            input.val(value - 1);
            updateCartItem($(this).data('item-id'), value - 1);
        }
    });
    
    $('.btn-plus').click(function() {
        var input = $(this).siblings('input');
        var value = parseInt(input.val());
        input.val(value + 1);
        updateCartItem($(this).data('item-id'), value + 1);
    });
    
    // Update cart item quantity via AJAX
    function updateCartItem(itemId, quantity) {
        $.ajax({
            url: '/cart/update/' + itemId + '/',
            type: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            data: {
                'quantity': quantity,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val() || $('meta[name=csrf-token]').attr('content')
            },
            success: function(response) {
                if (response.success) {
                    // Update the item total price if displayed
                    $('.item-total-' + itemId).text('$' + response.item_total);
                    $('.cart-total').text('$' + response.cart_total);
                    $('.cart-count').text(response.cart_items);
                } else {
                    alert(response.message || 'An error occurred');
                }
            },
            error: function() {
                alert('An error occurred. Please try again.');
            }
        });
    }
    
    // Auto-update cart on quantity change
    $('.quantity-input').on('change', function() {
        var $input = $(this);
        var itemId = $input.data('item-id');
        var quantity = parseInt($input.val());
        var maxStock = $input.data('max-stock');
        
        if (quantity < 1) {
            $input.val(1);
            quantity = 1;
        }
        
        if (quantity > maxStock) {
            alert('Only ' + maxStock + ' items available in stock!');
            $input.val(maxStock);
            quantity = maxStock;
        }
        
        if (itemId) {
            updateCartItem(itemId, quantity);
        }
    });
    
    // Wishlist toggle
    $('.wishlist-toggle').click(function(e) {
        e.preventDefault();
        var $button = $(this);
        var productId = $button.data('product-id');
        var isWishlisted = $button.hasClass('active');
        var $form = $button.closest('form');
        
        // If it's a form submission, let it submit normally
        if ($form.length && !$form.hasClass('ajax-wishlist')) {
            return true;
        }
        
        // Otherwise handle via AJAX
        $.ajax({
            url: '/wishlist/toggle/',
            type: 'POST',
            data: {
                'product_id': productId,
                'action': isWishlisted ? 'remove' : 'add',
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val() || $('meta[name=csrf-token]').attr('content')
            },
            success: function(response) {
                if (response.status === 'added') {
                    $button.addClass('active')
                        .find('i').removeClass('fa-heart-o').addClass('fa-heart');
                    $button.html('<i class="fas fa-heart"></i> Remove from Wishlist');
                } else if (response.status === 'removed') {
                    $button.removeClass('active')
                        .find('i').removeClass('fa-heart').addClass('fa-heart-o');
                    $button.html('<i class="fas fa-heart-o"></i> Add to Wishlist');
                }
            },
            error: function() {
                alert('An error occurred. Please try again.');
            }
        });
    });
    
    // Product image gallery
    $('.thumbnail').click(function() {
        var mainImage = $(this).data('image');
        $('.main-image').attr('src', mainImage);
        $('.thumbnail').removeClass('active');
        $(this).addClass('active');
    });
    
    // Add to cart with AJAX
    $('.add-to-cart').click(function(e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        var quantity = $('#quantity').val() || 1;
        
        $.ajax({
            url: '/cart/add/' + productId + '/',
            type: 'POST',
            data: {
                'quantity': quantity,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                // Update cart count
                var cartCount = parseInt($('.cart-count').text()) || 0;
                $('.cart-count').text(cartCount + parseInt(quantity));
                
                // Show success message
                showToast('Product added to cart!');
            }
        });
    });
    
    // Toast notification
    function showToast(message) {
        var toast = $('<div class="toast-alert">' + message + '</div>');
        $('body').append(toast);
        toast.css({
            'position': 'fixed',
            'top': '20px',
            'right': '20px',
            'background': '#28a745',
            'color': 'white',
            'padding': '1rem',
            'border-radius': '5px',
            'z-index': '9999'
        });
        
        setTimeout(function() {
            toast.fadeOut();
        }, 3000);
    }
    
    // Filter products
    $('#filter-form').on('change', function() {
        this.submit();
    });
    
    // Apply coupon
    $('#apply-coupon').click(function() {
        var couponCode = $('#coupon-code').val();
        if (couponCode) {
            $.ajax({
                url: '/cart/apply-coupon/',
                type: 'POST',
                data: {
                    'coupon_code': couponCode,
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.message);
                    }
                }
            });
        }
    });
    
    // Payment method toggle
    $('input[name="payment_method"]').change(function() {
        $('.payment-details').addClass('d-none');
        $('#' + $(this).val() + '-details').removeClass('d-none');
    });
    
    // Address form toggle
    $('#same-as-shipping').change(function() {
        if ($(this).is(':checked')) {
            $('#billing-address').slideUp();
        } else {
            $('#billing-address').slideDown();
        }
    });
});