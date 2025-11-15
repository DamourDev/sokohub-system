from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decorators import customer_required
# Create your views here.


@login_required
@customer_required
def checkout(request):
    pass



@login_required
@customer_required
def customer_orders(request):
    return render(request, 'orders/customer_orders.html')