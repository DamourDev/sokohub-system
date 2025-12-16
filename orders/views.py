from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators import customer_required, vendor_required
from products.models import Product
from .forms import CheckoutForm
from django.contrib import messages
from .models import Order, OrderItem
from products.cart import Cart
from django.db import transaction
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings 
# Create your views here.


@login_required
@customer_required
def checkout(request): 
    cart = Cart(request)
    
    # Validation: If cart is empty, redirect back
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('products_list')

    # GET Request: Display the Form with Pre-filled Data
    if request.method == 'GET':
        form = CheckoutForm(initial={
            'delivery_address': getattr(request.user, 'location', ''), # flexible getattr
            'phone': getattr(request.user, 'phone', '')
        })
        
        context = {
            'form': form,
            'cart': cart, 
            'total': cart.get_total_price(),
        }
        return render(request, 'orders/checkout.html', context)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            address = form.cleaned_data['delivery_address']
            phone = form.cleaned_data['phone']
            
            try:
                # TRANSACTION ATOMIC: Ensures strict data safety
                with transaction.atomic():
                    
                    # Create the PARENT Order (Customer's Receipt)
                    parent_order = Order.objects.create(
                        customer=request.user,
                        delivery_address=address,
                        phone=phone,
                        total=cart.get_total_price(),
                        status='pending',
                        parent=None, # No parent
                        vendor=None  # Mixed vendors
                    )

                    # Group Items by Vendor
                    vendor_buckets = {}
                    for item in cart:
                        product = item['product']
                        # Check Stock Level One Last Time
                        if product.stock < item['quantity']:
                            raise Exception(f"Sorry, {product.name} is out of stock.")
                            
                        vendor = product.vendor
                        if vendor not in vendor_buckets:
                            vendor_buckets[vendor] = []
                        vendor_buckets[vendor].append(item)

                    # Create CHILD Orders (Vendor's Copy)
                    for vendor, items in vendor_buckets.items():
                        vendor_subtotal = sum(item['total_price'] for item in items)
                        
                        child_order = Order.objects.create(
                            customer=request.user,
                            delivery_address=address,
                            phone=phone,
                            total=vendor_subtotal,
                            status='pending',
                            parent=parent_order, # Link to Parent
                            vendor=vendor        # Assign to Vendor
                        )
                        
                        # Create Order Items & Deduct Stock
                        for item in items:
                            product = item['product']
                            qty = item['quantity']
                            
                            OrderItem.objects.create(
                                order=child_order,
                                product=product,
                                quantity=qty,
                                price=item['price']
                            )
                            
                            # Deduct Stock
                            product.stock -= qty
                            product.save()

                    all_order_items = OrderItem.objects.filter(order__parent=parent_order)
                
                #  Prepare the Email Subject
                    subject = f"Order Confirmation - Invoice #{parent_order.id}"
                    
                    html_message = render_to_string('orders/order_invoice.html', {
                    'order': parent_order,
                    'items': all_order_items,
                    'user': request.user
                    })
                    
                    # 4. Create a Plain Text version (Best practice for spam filters)
                    plain_message = strip_tags(html_message)
                    
                    # 5. Send the Email
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL, # From email (in settings.py)
                        [request.user.email],        # To email
                        html_message=html_message,
                        fail_silently=False,
                    )

                    # Success! Clear Cart
                    
                    cart.cart.clear() 
                    cart.save()
                    
                    messages.success(request, f"Order #{parent_order.id} placed successfully!")
                    return redirect('order_confirmation', order_id=parent_order.id)

            except Exception as e:
                messages.error(request, f"Error processing order: {str(e)}")
                return redirect('checkout')
        
        else:
            # Form invalid
            messages.error(request, "Please check your details.")
            context = {
                'form': form,
                'cart': cart,
                'total': cart.get_total_price()
            }
            return render(request, 'orders/checkout.html', context)



@login_required
@customer_required
def customer_orders(request):

    orders = Order.objects.filter(customer=request.user, parent__isnull=True)\
                          .prefetch_related('sub_orders__items__product', 'sub_orders__vendor')\
                          .order_by('-created_at')

    
    search_query = request.GET.get('q')
    if search_query:
        orders = orders.filter(
            Q(sub_orders__items__product__name__icontains=search_query) |
            Q(id__icontains=search_query)
        )

    year_filter = request.GET.get('year')
    if year_filter:
        orders = orders.filter(created_at__year=year_filter)

    years = [2025, 2024, 2023, 2022, 2021, 2020]


    
    context = {
        'orders': orders,
        'years': years,
        'year_filter': year_filter,
        'search_query': search_query,
        'active_year': int(year_filter) if year_filter else None

    }

    return render(request, 'orders/customer_orders.html', context)



@login_required
@vendor_required
def vendor_orders(request):
    vendor = request.user
    
    # HANDLE STATUS UPDATE (POST Request)
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        
        # Verify this order belongs to this vendor before updating
        order_to_update = get_object_or_404(Order, id=order_id, vendor=vendor)
        
        order_to_update.status = new_status
        order_to_update.save()
        
        messages.success(request, f"Order #{order_id} marked as {new_status}")
        return redirect('vendor_orders') # Reload the page

    # FILTERING LOGIC 
    # We check the URL for ?status=pending or ?status=shipped
    status_filter = request.GET.get('status', 'all')
    
    # Get Child Orders assigned to this vendor
    orders = Order.objects.filter(vendor=vendor).select_related('customer').prefetch_related('items__product').order_by('-created_at')
    
    # Apply Filter
    if status_filter == 'pending':
        orders = orders.filter(status='pending')
    elif status_filter == 'shipped':
        orders = orders.filter(status__in=['shipped', 'delivered'])

    context = {
        'orders': orders,
        'active_filter': status_filter
    }

    return render(request, 'orders/vendor_orders.html', context)

@login_required
@customer_required
def order_confirmation(request, order_id):
    customer = request.user
    
    # Get the Parent Order (The wrapper)
    order = get_object_or_404(Order, id=order_id, customer=customer)

    
    # logic: Get all OrderItems where the related 'order' has 'parent' = current_order
    items = OrderItem.objects.filter(order__parent=order).select_related('product')

    context = {
        'order': order,
        'items': items
    }

    return render(request, 'orders/order_confirmation.html', context)


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    # Safety Check: Only allow if still pending
    if order.status == 'pending':
        # Cancel Parent
        order.status = 'cancelled'
        order.save()
        
        # Cancel all Sub-Orders (Shipments)
        for sub in order.sub_orders.all():
            sub.status = 'cancelled'
            sub.save()
            
            # RESTOCK ITEMS 
            for item in sub.items.all():
                item.product.stock += item.quantity
                item.product.save()

        messages.success(request, "Order cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled anymore as it is processing.")
    
    return redirect('customer_orders')