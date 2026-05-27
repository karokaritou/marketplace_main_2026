from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_seller = forms.BooleanField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        # Solo agregamos 'email' y 'is_seller'. 
        # UserCreationForm ya hereda y maneja las contraseñas automáticamente.
        fields = UserCreationForm.Meta.fields + ('email', 'is_seller')