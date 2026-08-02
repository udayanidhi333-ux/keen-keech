from django.db import models
from django.contrib.auth.models import User
import datetime
import secrets
import string


def generate_random_code(length=8):

    characters = string.ascii_uppercase + string.digits

    return ''.join(
        secrets.choice(characters)
        for _ in range(length)
    )

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(
        max_length=200
    )

    product_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional. Set this to show a strikethrough discount price (must be higher than the actual price)."
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to='products/'
    )

    stock = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    SIZE_CHOICES = [

        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
        ('XXXL', 'Triple Extra Large'),

    ]

    sizes = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: S,M,L,XL,XXL,XXXL"
    )

    size_chart = models.TextField(
        blank=True,
        help_text="Example: S:38:27:16.5,M:40:28:17,L:42:29:17.5"
    )


    def save(self, *args, **kwargs):

        if not self.product_code:

            while True:

                code = f"KK-PROD-{generate_random_code(8)}"

                if not Product.objects.filter(
                    product_code=code
                ).exists():

                    self.product_code = code

                    break

        super().save(*args, **kwargs)
    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def __str__(self):

        return f"{self.product_code} - {self.name}"

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    def __str__(self):
        return self.product.name



class ProductVariant(models.Model):
    VARIANT_TYPES = [
        ('SIZE', 'Size'),
        ('FABRIC', 'Fabric Type'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_type = models.CharField(max_length=10, choices=VARIANT_TYPES, default='SIZE')
    value = models.CharField(max_length=50, help_text="e.g. 38, 40, 42 or Premium Velvet, Pure Wool")
    stock = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - {self.get_variant_type_display()}: {self.value}"

class CustomerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    customer_id = models.CharField(
        max_length=15,
        unique=True,
        editable=False
    )

    name = models.CharField(
        max_length=100
    )

    whatsapp_number = models.CharField(
        max_length=15
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def save(self, *args, **kwargs):

        if not self.customer_id:

            while True:

                code = f"KKC-{generate_random_code(8)}"

                if not CustomerProfile.objects.filter(
                    customer_id=code
                ).exists():

                    self.customer_id = code

                    break

        super().save(*args, **kwargs)


    def __str__(self):

        return f"{self.customer_id} - {self.name}"


class Cart(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True)
class Wishlist(models.Model):
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} ❤️ {self.product.name}"

class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('payment pending', 'payment pending'),
        ('payment completed', 'payment completed')
    ]

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_CHOICES,
        default='payment pending'
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    shipping_address = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    tracking_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Add step-by-step production updates here."
    )

    order_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )


    def __str__(self):

        return f"Order #{self.order_number} - {self.customer.user.username}"


    def save(self, *args, **kwargs):

        if not self.order_number:

            while True:

                date_str = datetime.date.today().strftime('%Y%m')

                code = f"KK-{date_str}-{generate_random_code(8)}"

                if not Order.objects.filter(
                    order_number=code
                ).exists():

                    self.order_number = code

                    break

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10, blank=True)