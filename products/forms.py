from django import forms
from .models import Product

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ProductForm(forms.ModelForm):
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    class Meta:
        model = Product
        fields = ['category','name', 'description', 'price','unit', 'stock', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'rows': 4,'class': 'form-control', 'style': 'resize:none;', 'placeholder': 'Product details...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '..Frw'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g kg, litre, piece'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock
    
