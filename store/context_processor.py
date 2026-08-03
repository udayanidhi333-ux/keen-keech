from .models import Cart, CustomerProfile

def cart_count(request):
    cart_item_count = 0

    if request.user.is_authenticated:
        try:
            profile = CustomerProfile.objects.get(user=request.user)
            cart = Cart.objects.get(customer=profile)
            cart_item_count = sum(item.quantity for item in cart.items.all())
        except:
            cart_item_count = 0

    return {
        'cart_item_count': cart_item_count
    }