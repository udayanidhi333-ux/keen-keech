import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.http import Http404
from .models import Product, Cart, Wishlist, CartItem, CustomerProfile, Order, OrderItem ,Category
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST 
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q

def home(request):

    search = request.GET.get("q", "")

    products = Product.objects.all()

    if search:

        products = products.filter(
            models.Q(name__icontains=search) |
            models.Q(product_code__icontains=search) |
            models.Q(description__icontains=search)
        )

    products = products.order_by("-created_at")

    categories = Category.objects.all()

    cart_item_count = 0
    wishlist_products = []

    if request.user.is_authenticated:

        profile, _ = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        cart, _ = Cart.objects.get_or_create(
            customer=profile
        )

        wishlist_products = Wishlist.objects.filter(
            customer=profile
        ).values_list(
            "product_id",
            flat=True
        )

    else:

        if not request.session.session_key:
            request.session.create()

        cart, _ = Cart.objects.get_or_create(
            session_id=request.session.session_key
        )

    cart_item_count = sum(
        item.quantity
        for item in cart.items.all()
    )


    # CREATE CATEGORY SECTIONS

    category_sections = []

    for category in categories:

        category_items = products.filter(
            category=category
        )[:8]

        if category_items:

            category_sections.append({
                "category": category,
                "products": category_items,
            })


    return render(
        request,
        "store/home.html",
        {
            "products": products,
            "categories": categories,
            "category_sections": category_sections,
            "cart_item_count": cart_item_count,
            "wishlist_products": wishlist_products,
        }
    )

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # RELATED PRODUCTS
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    )[:4]
    # Convert "S,M,L,XL" into ["S", "M", "L", "XL"]
    sizes = []
    if product.sizes:
        sizes = [s.strip() for s in product.sizes.split(",")]

    # ---------- Size Chart ----------
    size_chart = []

    if hasattr(product, "size_chart") and product.size_chart:
        rows = product.size_chart.split(",")

        for row in rows:
            values = row.split(":")

            if len(values) == 4:
                size_chart.append({
                    "size": values[0].strip(),
                    "chest": values[1].strip(),
                    "length": values[2].strip(),
                    "shoulder": values[3].strip(),
                })

    # ---------- Cart Count ----------
    cart_item_count = 0

    if request.user.is_authenticated:
        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)
            cart = Cart.objects.get(customer=customer_profile)
            cart_item_count = sum(item.quantity for item in cart.items.all())
        except (CustomerProfile.DoesNotExist, Cart.DoesNotExist):
            cart_item_count = 0
    else:
        cart = request.session.get("cart", {})
        if isinstance(cart, dict):
            cart_item_count = sum(
                item.get("quantity", item) if isinstance(item, dict) else item
                for item in cart.values()
            )



    return render(request, "store/product_detail.html", {
        "product": product,
        "sizes": sizes,
        "size_chart": size_chart,
        "related_products": related_products,
        "cart_item_count": cart_item_count,
    })

def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:

        profile, _ = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        cart, _ = Cart.objects.get_or_create(
            customer=profile
        )

    else:

        if not request.session.session_key:
            request.session.create()

        cart, _ = Cart.objects.get_or_create(
            session_id=request.session.session_key
        )

    selected_size = request.POST.get("size", "")

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=selected_size,
    )

    if not created:
      quantity = int(request.POST.get("quantity", 1))

    cart_item.save()

    return redirect("cart_detail")



@require_POST
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')


@require_POST
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart_detail')


@require_POST
def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart_detail')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart_detail')

def cart_detail(request):

    if request.user.is_authenticated:

        profile, _ = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        cart, _ = Cart.objects.get_or_create(
            customer=profile
        )

    else:

        if not request.session.session_key:
            request.session.create()

        cart, _ = Cart.objects.get_or_create(
            session_id=request.session.session_key
        )

    cart_items = cart.items.all()

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    cart_item_count = sum(
        item.quantity
        for item in cart.items.all()
    )

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total,
        'cart_item_count': cart_item_count
    })


def proceed_to_checkout(request):

    # If customer is already logged in,
    # go directly to checkout

    if request.user.is_authenticated:

        return redirect('checkout')


    # Guest customer

    # Remember that they wanted to checkout

    request.session['checkout_after_register'] = 'checkout'


    # Send them to registration page

    return redirect('register')

def checkout(request):
    # MUST allow guest + logged in both
    if request.user.is_authenticated:
        customer_profile = CustomerProfile.objects.filter(user=request.user).first()

        if not customer_profile:
            customer_profile = CustomerProfile.objects.create(
                user=request.user,
                name=request.user.username,
                whatsapp_number="0000000000"
            )
        cart, _ = Cart.objects.get_or_create(customer=customer_profile)
    else:
        if not request.session.session_key:
            request.session.create()

        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)

        guest_user, _ = User.objects.get_or_create(username=f'guest_{request.session.session_key}')
        customer_profile, _ = CustomerProfile.objects.get_or_create(user=guest_user)

    cart_items = cart.items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        user_name = request.POST.get("full_name")
        user_phone = request.POST.get("phone_number")
        user_email = request.POST.get("email")

        house = request.POST.get("house")
        street = request.POST.get("street")
        area = request.POST.get("area")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")

        user_address = (
            f"{house}, {street}, {area}, "
            f"{city}, {state} - {pincode}"
        )

        customer_profile.name = user_name
        customer_profile.whatsapp_number = user_phone
        customer_profile.save()

        order = Order.objects.create(
            customer=customer_profile,
            total_amount=total_price,
            status='Pending',
            phone_number=user_phone,
            shipping_address=user_address
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                size=item.size
            )
        # ----------------------------
        # EMAIL TO STORE OWNER
        # ----------------------------

        items_text = ""

        for order_item in order.items.all():
            items_text += (
                f"Product : {order_item.product.name}\n"
                f"Size    : {order_item.size}\n"
                f"Quantity: {order_item.quantity}\n"
                f"Price   : ₹{order_item.price}\n\n"
            )

        subject = f"🛒 New Order Received - {order.order_number}"

        message = f"""
        A new order has been placed on Keen & Keech.

        Order Number:
        {order.order_number}

        Customer:
        {customer_profile.name}

        Phone:
        {order.phone_number}

        Shipping Address:
        {order.shipping_address}

        Products:
        {items_text}

        Total Amount:
        ₹{order.total_amount}
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ["udayanidhi333@gmail.com"],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Order confirmation email failed: {e}")
            
        # IMPORTANT: clear correct cart
        cart.items.all().delete()

                # ----------------------------
        # WhatsApp Share Link
        # ----------------------------

        items_text = ""

        for item in order.items.all():
            items_text += (
                f"• {item.product.name}"
                f" ({item.size})"
                f" x{item.quantity}\n"
            )

        whatsapp_message = f"""
        Hello  Keen & Keech,

        i have successfully placed an order.

        Order Number:
        {order.order_number}

        Customer:
        {customer_profile.name}

        Phone:
        {order.phone_number}

        Products:
        {items_text}

        Total:
        ₹{order.total_amount}
        """

        shop_whatsapp_url = (
            "https://wa.me/918122311196?"
            "text=" + urllib.parse.quote(whatsapp_message)
        )

        return render(request, 'store/order_success.html', {
            'order': order,
            'shop_whatsapp_url': shop_whatsapp_url,
        })

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_detail.html', {
        'order': order, 
        'order_items': OrderItem.objects.filter(order=order)
    })

@login_required


def customer_orders(request):

    customer = CustomerProfile.objects.filter(
        user=request.user
    ).first()

    if not customer:
        return render(request, "store/customer_orders.html", {
            "orders": []
        })

    orders = (Order.objects.filter(
        customer=customer).prefetch_related("items__product")
    ).order_by("-created_at")

    return render(request, "store/customer_orders.html", {
        "orders": orders
    })

@login_required
def wishlist(request):
    customer = get_object_or_404(CustomerProfile, user=request.user)

    wishlist_items = Wishlist.objects.filter(
        customer=customer
    ).select_related("product")

    return render(request, "store/wishlist.html", {
        "wishlist_items": wishlist_items
    })


@login_required
def add_to_wishlist(request, product_id):

    customer = get_object_or_404(
        CustomerProfile,
        user=request.user
    )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    Wishlist.objects.get_or_create(
        customer=customer,
        product=product
    )

    # Go back to the same page
    next_url = request.META.get("HTTP_REFERER", "/")

    # Keep the browser at the Collections section
    if "#collection" not in next_url:
        next_url += "#collection"

    return redirect(next_url)


@login_required
def remove_from_wishlist(request, wishlist_id):
    item = get_object_or_404(
        Wishlist,
        id=wishlist_id,
        customer__user=request.user
    )

    item.delete()

    return redirect(request.META.get("HTTP_REFERER", "wishlist"))


@staff_member_required
def staff_dashboard(request):
    orders = Order.objects.all().order_by('-created_at')
    if request.method == 'POST':
        order_obj = get_object_or_404(Order, id=request.POST.get('order_id'))
        order_obj.status = request.POST.get('status')
        order_obj.save()
        return redirect('staff_dashboard')
    return render(request, 'store/staff_dashboard.html', {'orders': orders})

def register(request):

    if request.user.is_authenticated:
        return redirect('home')


    # Save the guest session ID BEFORE registration

    guest_session_id = request.session.session_key


    if request.method == 'POST':

        form = RegisterForm(request.POST)


        if form.is_valid():

            # CREATE USER

            user = form.save(commit=False)

            user.set_password(
                form.cleaned_data['password1']
            )

            user.save()


            # CREATE CUSTOMER PROFILE

            customer_profile, created = CustomerProfile.objects.update_or_create(

                user=user,

                defaults={

                    'name': form.cleaned_data['name'],

                    'whatsapp_number':
                    form.cleaned_data['whatsapp_number']

                }

            )


            # LOGIN THE NEW USER

            login(request, user)


            # FIND THE OLD GUEST CART

            if guest_session_id:

                guest_cart = Cart.objects.filter(

                    session_id=guest_session_id

                ).first()


                if guest_cart:

                    # CREATE CUSTOMER CART

                    customer_cart, created = Cart.objects.get_or_create(

                        customer=customer_profile

                    )


                    # MOVE EACH PRODUCT FROM GUEST CART

                    for guest_item in guest_cart.items.all():

                        customer_item, item_created = \
                        CartItem.objects.get_or_create(

                            cart=customer_cart,

                            product=guest_item.product,

                            size=guest_item.size,

                            defaults={

                                'quantity':
                                guest_item.quantity

                            }

                        )


                        # If product already exists,
                        # add the quantities together

                        if not item_created:

                            customer_item.quantity += \
                            guest_item.quantity

                            customer_item.save()


                    # DELETE OLD GUEST CART

                    guest_cart.delete()


            messages.success(

                request,

                "Welcome to KEEN & KEECH!"

            )


            # GO BACK TO CHECKOUT

            next_url = request.session.pop(

                'checkout_after_register',

                None

            )


            if next_url:

                return redirect(next_url)


            return redirect('home')


    else:

        form = RegisterForm()


    return render(

        request,

        'store/register.html',

        {

            'form': form

        }

    )

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())

            messages.success(request, "Login Successful")

            return redirect('home')

    else:
        form = LoginForm()

    return render(request, 'store/login.html', {
        'form': form
    })




@login_required
def account(request):
    customer, _ = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "whatsapp_number": ""
        }
    )

    return render(request, "store/account.html", {
        "customer": customer
    })


def search_products(request):

    products = Product.objects.all().order_by("-created_at")

    category = request.GET.get("category")
    q = request.GET.get("q")

    if category:
        products = products.filter(category__slug=category)

    if q:
        products = products.filter(name__icontains=q)

    html = render_to_string(
        "store/includes/product_grid.html",
        {
            "products": products,
            "wishlist_products": request.session.get("wishlist", []),
        },
        request=request
    )

    return JsonResponse({
        "html": html
    })

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")

def about(request):
    return render(request, "store/about.html")

def contact(request):
    return render(request, 'store/contact.html')