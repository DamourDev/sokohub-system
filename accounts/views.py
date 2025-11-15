from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login,logout 
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST) 
        if form.is_valid(): 
            user = form.save()

            messages.success(request, "Account created successfully! Welcome to SokoHub.")
            
            login(request, user)  # Log the user in after registration

            if user.user_type == 'vendor':
                return redirect('vendor_dashboard')  # Redirect to vendor dashboard
            else:
                return redirect('product_list')  # Redirect to product listing for customers
        
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form}) 



def login_view(request):
    if request.user.is_authenticated:

        if request.user.user_type == 'vendor':
            return redirect('vendor_dashboard')
        else:
            return redirect('product_list')
        
    form = LoginForm(request.POST or None) 

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')

            user = authenticate(username=username, password=password)

            if user:
                login(request, user)

                # Handle "Remember Me"
                if remember_me:
                    request.session.set_expiry(3600)  # 1 hour
                else:
                    request.session.set_expiry(0)  # Session expires on browser close

                messages.success(request, f"Welcome back, {user.username}!")

                # Redirect based on user_type
                if user.user_type == 'vendor':
                    return redirect('vendor_dashboard')
                else:
                    return redirect('product_list')
            else:
                # Form validation already handles this, but extra safety
                messages.error(request, "Invalid username or password.")

    context = {'form': form}
    return render(request, 'accounts/login.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')
