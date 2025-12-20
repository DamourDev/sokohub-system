from django import forms
from allauth.account.forms import SignupForm, LoginForm
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class CustomSignupForm(SignupForm):

    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('customer', 'Customer')
    )

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.Select()
    )

    phone = forms.CharField(
        required=True,
        widget=forms.TextInput()
    )

    location = forms.CharField(
        required=True,
        widget=forms.TextInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'] = forms.CharField(
            max_length=150,
            required=True,
            widget=forms.TextInput()
        )

        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
            field.widget.attrs.setdefault('placeholder', field.label)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def save(self, request):
        user = super().save(request)

        # Custom fields (kept)
        user.phone = self.cleaned_data['phone']
        user.location = self.cleaned_data['location']
        user.user_type = self.cleaned_data['user_type']
        user.save()

        # Email (kept)
        subject = "Welcome to SokoHub!"
        message = render_to_string(
            'accounts/signup_success_email.html',
            {'user': user}
        )

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=message,
            fail_silently=True
        )

        if request:
            request.session['post_signup_redirect'] = (
                'vendor_dashboard'
                if user.user_type == 'vendor'
                else 'products_list'
            )

        return user


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['login'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })

        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'location']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
        }
