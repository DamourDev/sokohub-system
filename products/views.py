from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decorators import vendor_required

# Create your views here.

@login_required
@vendor_required
def vendor_dashboard(request):
    return render(request, 'products/vendor_dashboard.html')

@login_required
def product_list(request):
    return render(request, 'products/product_list.html')    
