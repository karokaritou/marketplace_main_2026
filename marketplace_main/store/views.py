from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import RegisterForm, ProductForm
from .models import Product

# ==========================================
# 🏠 Catálogo y Vistas Públicas
# ==========================================

def home(request):
    # select_related y prefetch_related optimizan las consultas para evitar problemas de rendimiento (N+1)
    products = Product.objects.select_related('owner').prefetch_related('categories').all()
    return render(request, 'marketplace/home.html', {'products': products})


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

    # Validamos explícitamente el POST antes de procesar el formulario
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        form.save_m2m()  # Necesario para guardar las categorías ManyToMany de forma segura

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