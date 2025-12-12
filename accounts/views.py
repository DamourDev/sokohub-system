from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login,logout 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from  django.conf import settings
from .models import EmailOTP
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice 
from .forms import UserUpdateForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView


User = get_user_model() 


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST) 
        if form.is_valid(): 
            user = form.save()

            if user.email:
                subject = 'Welcome to SokoHub!'
                message = f"Hi {user.username},\n\nCongratulations! You are now a registered member of SokoHub.\n\nYou can now browse products and place orders.\n\nThank you for joining us!"
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [user.email]

                try:
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    print(f"Error sending email: {e}")

            messages.success(request, "Account created successfully! Welcome to SokoHub.")
            
            login(request, user)  # Log the user in after registration

            if user.user_type == 'vendor':
                return redirect('vendor_dashboard')  # Redirect to vendor dashboard
            else:
                return redirect('products_list')  # Redirect to product listing for customers
        
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
            return redirect('products_list')
        
    form = LoginForm(request.POST or None) 

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')

            user = authenticate(username=username, password=password)

            if user:

                if user.mfa_enabled:
                    request.session['pre_mfa_user_id'] = user.id

                    if user.mfa_method == 'email':
                        
                        otp, _ = EmailOTP.objects.get_or_create(user=user)
                        otp.generate_code()

                        if user.email:
                            try:
                                send_mail(
                                    'SokoHub Verification Code',
                                    f'Your code is: {otp.otp_code}',
                                    settings.EMAIL_HOST_USER,
                                    [user.email],
                                    fail_silently=False
                                )
                                messages.info(request, "Code sent to your email.")
                            except Exception as e:
                                messages.error(request, "Email failed to send.")
                        
                        return redirect('verify_mfa')
                    
                    elif user.mfa_method == 'app':
                        return redirect('verify_mfa')
                    
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
                    return redirect('products_list')
            else:
                # Form validation already handles this, but extra safety
                messages.error(request, "Invalid username or password.")

    context = {'form': form}
    return render(request, 'accounts/login.html', context)




def verify_mfa(request):
    user_id = request.session.get('pre_mfa_user_id')
    
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        code = request.POST.get('otp_code')
        is_verified = False

        # Check the code based on their method
        if user.mfa_method == 'app':
            # Check against App (TOTP)
            device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
            if device and device.verify_token(code):
                is_verified = True
        
        elif user.mfa_method == 'email':
            # Check against Email OTP
            try:
               
                if user.email_otp.is_valid() and user.email_otp.otp_code == code:
                    is_verified = True
            except EmailOTP.DoesNotExist:
                print ("No EmailOTP found for user.")
                is_verified = False

        
        if is_verified:
            # SUCCESS: Log them in and clear the session
            login(request, user)
            del request.session['pre_mfa_user_id']
            
            messages.success(request, "Verification successful!")
            if user.user_type == 'vendor':
                return redirect('vendor_dashboard')
            else:
                return redirect('products_list')
        else:
            messages.error(request, "Invalid code. Please try again.")

    context = {
        'mfa_method': user.mfa_method
    }

    return render(request, 'accounts/verify_mfa.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        
        if form.is_valid():
            user = form.save()
            
            if user.email:
                subject = 'SokoHub Profile Update'
                message = f"Hello {user.username},\n\nYour profile information was updated successfully on {settings.EMAIL_HOST_USER}."
                
                try:
                    send_mail(
                        subject, 
                        message, 
                        settings.EMAIL_HOST_USER, 
                        [user.email], 
                        fail_silently=True 
                    )
                except Exception as e:
                    print(f"Email error: {e}")

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('landing_page') 
            
    else:
        # GET request: Load the form with existing user data
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})

class ChangePasswordView(PasswordChangeView):
    template_name = 'accounts/change_password.html'

    # using reverse_lazy to avoid circular import issues
    success_url = reverse_lazy('landing_page')

    def form_valid(self, form):
        
        response = super().form_valid(form)
        user = self.request.user
        if user.email:
            subject = 'Security Alert: Password Changed'
            message = f"Hello {user.username},\n\nYour SokoHub password was just changed. If this wasn't you, please contact support immediately."
            
            try:
                send_mail(
                    subject, 
                    message, 
                    settings.EMAIL_HOST_USER, 
                    [user.email], 
                    fail_silently=True 
                )
            except Exception as e:
                print(f"Email error: {e}")

        messages.success(self.request, 'Your password has been changed successfully!')

        return response


@login_required
def mfa_settings(request):
    user = request.user

    has_app_device = TOTPDevice.objects.filter(user=user, confirmed=True).exists() 

    context = { 
        'is_mfa_enabled': user.mfa_enabled,
        'current_method': user.mfa_method,
        'has_app_device': has_app_device,
    }
    return render(request, 'accounts/mfa_settings.html', context)      
            

@login_required
def enable_email_mfa(request):
    user = request.user
    
    otp, _ = EmailOTP.objects.get_or_create(user=user)
    
    # This generates the number, sets the time, sets expiry, and saves it.
    otp.generate_code()
    
    subject = 'Verify your Email for Two-Factor Auth'
    message = f"Your verification code is: {otp.otp_code}"
    
    try:
        send_mail(
            subject, 
            message, 
            settings.EMAIL_HOST_USER, 
            [user.email], 
            fail_silently=True
        )
    except Exception as e:
        messages.error(request, "Failed to send email. Please try again.")
        return redirect('mfa_settings')

    # 4. Redirect to verification
    return redirect('verify_email_setup')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import EmailOTP

@login_required
def verify_email_setup(request):
    if request.method == 'POST':
        code = request.POST.get('otp_code')
        user = request.user
        
        try:
            otp = EmailOTP.objects.get(user=user)
            
            if otp.otp_code == code and otp.is_valid():
             
                # Update User Profile
                user.mfa_enabled = True
                user.mfa_method = 'email'
                user.save()
                
                # 2. Clean up the used code 
                otp.otp_code = "" 
                
                messages.success(request, "Success! Email Two-Factor Authentication is enabled.")
                return redirect('mfa_settings')
                
            else:
                # Code matches but expired OR Code is wrong
                if not otp.is_valid():
                    messages.error(request, "This code has expired. Please try enabling again.")
                else:
                    messages.error(request, "Invalid code. Please try again.")

        except EmailOTP.DoesNotExist:
            messages.error(request, "No verification pending. Please start over.")
            return redirect('mfa_settings')

    return render(request, 'accounts/verify_email_setup.html')