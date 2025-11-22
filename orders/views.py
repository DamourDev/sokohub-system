from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators import customer_required, vendor_required
from products.models import Product
from .forms import CheckoutForm
from django.contrib import messages
from .models import Order, OrderItem
# Create your views here.


@login_required
@customer_required
def checkout(request, pk): 
    quantity = 1

    if request.method == 'GET':

        quantity = int(request.GET.get('quantity', 1))
        form = CheckoutForm(initial={
            'delivery_address': request.user.location,
            'phone': request.user.phone
        })

    product = get_object_or_404(Product, pk=pk)
    if product.stock > 0:
        quantity_range = range(1, product.stock + 1)
    else:
        quantity_range = []

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        quantity = int(request.POST.get('quantity', 1)) 
        if form.is_valid():
            order = Order.objects.create(
                customer=request.user,
                delivery_address=form.cleaned_data['delivery_address'],
                phone=form.cleaned_data['phone'],
                total=product.price * quantity

            )
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            product.stock -= quantity
            product.save()
            messages.success(request, f"Order placed successfully! Your order ID is {order.id}.")

            return redirect('order_confirmation', order_id=order.id)
        
    

    context = {
        'form': form,
        'product': product,
        'quantity_range': quantity_range,
        'quantity': quantity,
        'total': product.price * quantity
        
    }

    return render(request, 'orders/checkout.html', context)
    



@login_required
@customer_required
def customer_orders(request):

    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    context = {
        'orders': orders
    }

    return render(request, 'orders/customer_orders.html', context)

@login_required
@vendor_required
def vendor_orders(request):

    vendor = request.user

    items = OrderItem.objects.filter(product__vendor=vendor).select_related('order', 'product').order_by('-order__created_at')

    context = {
        'items': items 
    }

    return render(request, 'orders/vendor_orders.html', context)


@login_required
@customer_required
def order_confirmation(request, order_id):
    customer=request.user
    order = get_object_or_404(Order, id=order_id, customer=customer)

    items = order.items.all()

    context = {
        'order': order,
        'items': items
    }

    return render(request, 'orders/order_confirmation.html', context)
    