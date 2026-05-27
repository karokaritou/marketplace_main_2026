from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import RegisterForm, ProductForm
from .models import Product, Cart, CartItem, Category

# ==========================================
# 🏠 Catálogo y Vistas Públicas (Búsqueda, Filtros y Paginación)
# ==========================================

def home(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    # Base de la consulta optimizada (Evita problema N+1)
    products = Product.objects.select_related('owner').prefetch_related('categories').all()

    # =========================
    # 🔎 Búsqueda por Texto
    # =========================
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # =========================
    # 🏷️ Filtro por Categoría
    # =========================
    if category_id:
        products = products.filter(
            categories__id=category_id
        )

    # =========================
    # 📄 Paginación (6 productos por página)
    # =========================
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Necesario para pintar los botones de filtro en la barra lateral o barra de búsqueda
    categories = Category.objects.all()

    return render(request, 'marketplace/home.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'current_category': category_id
    })


# ==========================================
# 🔐 Autenticación de Usuarios
# ==========================================

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'marketplace/register.html', {'form': form})


def login_view(request):
    error_msg = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_msg = "Usuario o contraseña incorrectos."

    return render(request, 'marketplace/login.html', {'error': error_msg})


def logout_view(request):
    logout(request)
    return redirect('home')


# ==========================================
# 📊 Panel de Control y CRUD (Solo Vendedores)
# ==========================================

@login_required
def dashboard(request):
    if not request.user.is_seller:
        return HttpResponseForbidden("No tienes permisos")

    products = Product.objects.filter(owner=request.user)

    return render(request, 'store/dashboard.html', {
        'products': products
    })


@login_required
def product_create(request):
    if not request.user.is_seller:
        return HttpResponseForbidden("Solo vendedores")

    form = ProductForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        form.save_m2m()

        return redirect('dashboard')

    return render(request, 'store/product_form.html', {'form': form})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.owner != request.user:
        return HttpResponseForbidden("No puedes editar este producto")

    form = ProductForm(request.POST or None, instance=product)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('dashboard')

    return render(request, 'store/product_form.html', {'form': form, 'product': product})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.owner != request.user:
        return HttpResponseForbidden("No puedes eliminar este producto")

    if request.method == 'POST':
        product.delete()
        return redirect('dashboard')

    return render(request, 'store/product_confirm_delete.html', {'product': product})


# ==========================================
# 🛒 Carrito de Compras (Solo Compradores Logueados)
# ==========================================

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.select_related('product')

    return render(request, 'marketplace/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items
    })


@login_required
def add_to_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_detail')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )
    item.delete()

    return redirect('cart_detail')


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()
        except (ValueError, TypeError):
            pass

    return redirect('cart_detail')