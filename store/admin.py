from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
    CustomerProfile,
    Cart,
    CartItem,
    Wishlist,
    Order,
    OrderItem
)


# ==========================================
# PRODUCT IMAGE INLINE
# ==========================================

class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 1

    fields = (
        "image",
    )


# ==========================================
# PRODUCT VARIANT INLINE
# ==========================================

class ProductVariantInline(admin.TabularInline):

    model = ProductVariant

    extra = 1

    fields = (
        "variant_type",
        "value",
        "stock",
    )


# ==========================================
# PRODUCT ADMIN
# ==========================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "product_code",
        "name",
        "category",
        "price",
        "stock",
        "created_at",
    )

    list_display_links = (
        "product_code",
        "name",
    )

    search_fields = (
        "product_code",
        "name",
        "description",
    )

    list_filter = (
        "category",
        "created_at",
    )

    list_editable = (
        "price",
        "stock",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "product_code",
        "created_at",
    )

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]


# ==========================================
# CATEGORY ADMIN
# ==========================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
    )

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": (
            "name",
        )
    }


# ==========================================
# CUSTOMER PROFILE ADMIN
# ==========================================

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "customer_id",
        "name",
        "whatsapp_number",
        "created_at",
    )

    search_fields = (
        "customer_id",
        "name",
        "whatsapp_number",
    )

    ordering = (
        "-created_at",
    )


# ==========================================
# WISHLIST ADMIN
# ==========================================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        "customer",
        "product",
        "created_at",
    )

    search_fields = (
        "customer__name",
        "product__name",
    )

    list_filter = (
        "created_at",
    )


# ==========================================
# ORDER ITEM INLINE
# ==========================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "product",
        "quantity",
        "price",
        "size",
    )


# ==========================================
# ORDER ADMIN
# ==========================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "customer",
        "total_amount",
        "status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "customer__name",
        "customer__whatsapp_number",
    )

    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )

    readonly_fields = (
        "order_number",
        "created_at",
    )

    inlines = [
        OrderItemInline,
    ]

    ordering = (
        "-created_at",
    )


# ==========================================
# OTHER MODELS
# ==========================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "session_id",
        "created_at",
    )

    search_fields = (
        "session_id",
        "customer__name",
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "product",
        "quantity",
        "size",
    )

    search_fields = (
        "product__name",
        "product__product_code",
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "variant_type",
        "value",
        "stock",
    )

    list_filter = (
        "variant_type",
    )

    search_fields = (
        "product__name",
        "value",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product",
        "quantity",
        "price",
        "size",
    )

    search_fields = (
        "order__order_number",
        "product__name",
    )