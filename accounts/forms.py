from django import forms
from allauth.account.forms import SignupForm, LoginForm
from .models import CustomUser


class CustomSignupForm(SignupForm):
    # 1. DEFINE YOUR CUSTOM FIELDS
    # (Username, Email, Password are handled automatically by the parent SignupForm)
    
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('customer', 'Customer')
    )

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.Select(), 
    )
    
    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '07....'})
    )
    
    location = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Location'})
    )

    def __init__(self, *args, **kwargs):
        """
        This matches your old widget logic:
        It adds 'class="form-control"' to every field (including Username/Password)
        so they look exactly like your old form.
        """
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
            # Use the field's label as a placeholder if one isn't set
            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = field.label

    def save(self, request):
        # 1. Let allauth create the user object
        user = super(CustomSignupForm, self).save(request)
        
        # 2. Add your custom data
        user.phone = self.cleaned_data['phone']
        user.location = self.cleaned_data['location']
        user.user_type = self.cleaned_data['user_type']
        
        # 3. Save to database
        user.save()
        return user

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        
        # Style the 'login' field (Username/Email)
        self.fields['login'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
        
        # Style the 'password' field
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
# We keep your UserUpdateForm exactly as it was for profile editing
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'location']
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
        }