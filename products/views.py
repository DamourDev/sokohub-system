from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators import vendor_required
from products.models import Product, ProductGallery, Category
from orders.models import Order
from .forms import ProductForm
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import MultipleFileInput
from django import forms
from django.http import JsonResponse
from .cart import Cart 
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your views here.

@login_required
@vendor_required
def vendor_dashboard(request):
    form = ProductForm()
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
    recent_products = Product.objects.filter(vendor=vendor, is_deleted=False).prefetch_related('gallery_images').order_by('-created_at')[:8
    ]
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'out_of_stock_products': out_of_stock_products,
        'pending_orders': pending_orders,
        'recent_products': recent_products,
        'form': form,
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

            # Handling multiple gallery images
            images = request.FILES.getlist('gallery_images')
            for image in images:
                if image:
                    ProductGallery.objects.create(product=product, image=image)


            messages.success(request, 'Product added successfully!')
            return redirect('vendor_products_list')

        else:
            print(form.errors)

            form.fields['gallery_images'] = forms.FileField(
            widget=MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}),
            required=False,
            label='Gallery Images'
        )

    else:
        form = ProductForm()

    form.fields['gallery_images'] = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False,
        label='Gallery Images'
    )   
        
    
    return render(request, 'products/product_form.html', {'form': form})

@login_required
@vendor_required
def vendor_products_list(request):
    form = ProductForm()

    vendor = request.user 
    products = Product.objects.filter(status='active', vendor=vendor).prefetch_related('gallery_images').order_by('-created_at')
    context = {
        'products': products,
        'form': form,
        
    }
    
    return render(request, 'products/vendor_products_list.html', context)

 

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
    
    gallery = product.gallery_images.all()

    # Logic: Determine if we show a Dropdown or a Text Input
    show_manual_input = False
    quantity_range = []

    if product.stock > 12:
        # If stock is greater than 12, we allow the user to type the number manually
        show_manual_input = True
        
    elif product.stock > 0:
        # If stock is between 1 and 12, we provide a specific range for the dropdown
        show_manual_input = False
        quantity_range = range(1, product.stock + 1)
        
    else:
        # Stock is 0 (Out of stock)
        quantity_range = []

    context = {
        'product': product,
        'gallery': gallery,             
        'show_manual_input': show_manual_input, 
        'quantity_range': quantity_range,      
    }

    return render(request, 'products/product_detail.html', context)


def vendor_public_products(request, vendor_id):

    vendor = get_object_or_404(User, pk=vendor_id)
    products = Product.objects.filter(vendor=vendor, status='active').order_by('-created_at')
    context = {
        'products': products,
        'vendor': vendor,
    }
    return render(request, 'products/vendor_public_products.html', context)


@login_required
@vendor_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)

    if request.method ==  'POST':
        product.is_deleted = True
        product.save()
        messages.success(request, 'Product deleted successfully!')
        
        return redirect(request.META.get('HTTP_REFERER', 'vendor_dashboard'))
    
    return redirect('vendor_dashboard')
    

@login_required
@vendor_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # Handle multiple gallery images
            images = request.FILES.getlist('gallery_images')
            for image in images:
                ProductGallery.objects.create(product=product, image=image)

            messages.success(request, 'Product updated successfully!')
            return redirect('vendor_products_list')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'action': 'edit',
    }

    return render(request, 'products/product_form.html',context)


def related_products_list(request, pk):
    source_product = get_object_or_404(Product, pk=pk)
    category = source_product.category
    related_list = Product.objects.filter(category=category)
    
    paginator = Paginator(related_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'source_product': source_product,
        'related_list': related_list,
        'category': category,
    }

    return render(request, 'products/related_products_list.html', context)



# 1. ADD / INCREMENT View
def cart_add(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product = get_object_or_404(Product, id=product_id)
        
        # Add to cart (Logic: +1)
        cart.add(product=product)
        
        # Get updated data to send back to JS
        cart_qty = cart.__len__()
        cart_total = cart.get_total_price()
        
        # Use the session dictionary to find the quantity of THIS specific item
        # We need this so the number between (-) and (+) updates instantly
        item_qty = cart.cart[str(product_id)]['quantity']
        image_url = product.image.url if product.image else 'No image available'
        response = JsonResponse({
            'qty': item_qty, 
            'cart_qty': cart_qty, 
            'cart_total': cart_total,
            'product': 
            {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image': image_url,
            }

        })
        return response

# 2. DECREMENT View
def cart_decrement(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product = get_object_or_404(Product, id=product_id)
        
        # Decrease quantity (Logic: -1, stops at 1)
        cart.decrement(product=product)
        
        cart_qty = cart.__len__()
        cart_total = cart.get_total_price()
        item_qty = cart.cart[str(product_id)]['quantity']
        
        response = JsonResponse({
            'qty': item_qty,
            'cart_qty': cart_qty,
            'cart_total': cart_total
        })
        return response

# 3. REMOVE View
def cart_remove(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product = get_object_or_404(Product, id=product_id)
        
        # Remove completely
        cart.remove(product)
        
        cart_qty = cart.__len__()
        cart_total = cart.get_total_price()
        
        response = JsonResponse({
            'cart_qty': cart_qty, 
            'cart_total': cart_total
        })
        return response