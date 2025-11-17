from functools import wraps
from django.shortcuts import redirect  
from django.contrib import messages

def vendor_required(view_func):
    @wraps(view_func) 
    def wrapper(request, *args, **kwargs):
        if request.user.user_type == 'vendor':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Only vendor can access this page.")
            return redirect('login')
        
    return wrapper


def customer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.user_type == 'customer':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Only customers can access this page.")
            return redirect('login')
        
    return wrapper