from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators import vendor_required
from products.models import Product
from orders.models import Order
from .forms import ProductForm
from django.contrib import messages
from django.core.paginator import Paginator
# from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
User = get_user_model()
# Create your views here.

@login_required
@vendor_required
def vendor_dashboard(request):
    vendor = request.user
    # counting all products belonged to the vendor
    total_products = Product.objects.filter(vendor=vendor).count()

    #counting active products
    active_products = Product.objects.filter(vendor=vendor, status='active').count()

    #count of out of stock products
    out_of_stock_products = Product.objects.filter(vendor=vendor, stock=0).count()
    #count of pending orders for the vendor
    pending_orders = Order.objects.filter(
        items__product__vendor=vendor,
        status='pending'
    ).distinct().count()

    # 5 recent products added by the vendor
    recent_products = Product.objects.filter(vendor=vendor).order_by('-created_at')[:5]
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'out_of_stock_products': out_of_stock_products,
        'pending_orders': pending_orders,
        'recent_products': recent_products,
    }

    return render(request, 'products/dashboard.html', context)


@login_required
@vendor_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('vendor_products_list')

    else:
        form = ProductForm()
    
    return render(request, 'products/add_product.html', {'form': form})

@login_required
@vendor_required
def vendor_products_list(request):
    vendor = request.user
    products = Product.objects.filter(status='active', vendor=vendor).order_by('-created_at')
    return render(request, 'products/vendor_products_list.html', {'products': products})

 

def products_list(request): 
    
    products =  Product.objects.filter(status='active')

    sort_option = request.POST.get('sort', 'newest')

    if sort_option == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_option == 'price_high_to_low':
        products = products.order_by('-price')

    else:
        products = products.order_by('-created_at')


    # apply pagination : 12 products per page

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj, 
        'sort_option': sort_option,
    }

    return render(request, 'products/products_list.html', context)

 

def landing_page(request):
    
    products = Product.objects.filter(status='active').order_by('-created_at')[:8]

    context = {
        'products': products,
    }

    return render(request, 'products/landing_page.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.stock > 0:
        quantity_range = range(1, product.stock + 1)

    else:
        quantity_range = []

    context = {
        'product': product,
        'quantity_range': quantity_range,
    }

    return render(request, 'products/product_detail.html',context)


def vendor_public_products(request, vendor_id):

    vendor = get_object_or_404(User, pk=vendor_id)
    products = Product.objects.filter(vendor=vendor, status='active').order_by('-created_at')
    context = {
        'products': products,
        'vendor': vendor,
    }
    return render(request, 'products/vendor_public_products.html', context)