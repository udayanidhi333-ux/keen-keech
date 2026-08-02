from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path("category/<slug:slug>/",views.category_products,name="category_products"),

    path("category-filter/",views.category_filter, name="category_filter"),

    path("search/", views.search_products, name="search_products"),

    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/', views.cart_detail, name='cart_detail'),

    path('proceed-to-checkout/',views.proceed_to_checkout, name='proceed_to_checkout'),

    path('checkout/', views.checkout, name='checkout'),

    path('my-orders/', views.customer_orders, name='customer_orders'),

    path('my-orders/<str:order_number>/', views.order_detail, name='order_detail'),

    path('studio-panel/', views.staff_dashboard, name='staff_dashboard'),

    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # NEW
    path('increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),

    path('decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),

    path('delete/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),

    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),

    path(
        'wishlist/add/<int:product_id>/',
        views.add_to_wishlist,
        name='add_to_wishlist'
    ),

    path(
        'wishlist/remove/<int:wishlist_id>/',
        views.remove_from_wishlist,
        name='remove_from_wishlist'
    ),
    # Login/Register
    path('login/', views.user_login, name='login'),

    path('register/', views.register, name='register'),

    path('account/', views.account, name='account'),

    path('logout/', views.user_logout, name='logout'),

    path('about/', views.about, name='about'),

    path('contact/', views.contact, name='contact'),

]