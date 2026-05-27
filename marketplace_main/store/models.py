import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# =========================
# 👤 Usuario Custom
# =========================
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# =========================
# 🏷️ Categoría
# =========================
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# =========================
# 📦 Producto
# =========================
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products'
    )  # Relación 1:N

    categories = models.ManyToManyField(
        Category,
        related_name='products'
    )  # Relación N:M

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# 🛒 Carrito
# =========================
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts'
    )  # Relación 1:N

    products = models.ManyToManyField(
        Product,
        through='CartItem',
        related_name='carts'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🧠 Propiedad Dinámica: Calcula el precio total sumando los subtotales de sus items
    @property
    def total(self):
        return sum(item.subtotal for item in self.cartitem_set.all())

    def __str__(self):
        return f"Cart {self.id} - {self.user.username}"


# =========================
# 🧾 CartItem (Tabla Intermedia)
# =========================
class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')  # Evita productos duplicados en el mismo carrito

    # 🧠 Propiedad Dinámica: Calcula el subtotal por producto
    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"