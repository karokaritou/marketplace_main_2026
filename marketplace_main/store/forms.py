from django import forms
from .models import User, Product

class RegisterForm(forms.ModelForm):
    # (Tu código de RegisterForm aquí...)
    pass

# ASEGÚRATE DE QUE ESTO ESTÉ ESCRITO ASÍ:
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple()
        }