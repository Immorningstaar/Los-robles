from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Residente


# 🔐 LOGIN
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='RUT',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su RUT'
        })
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '********'
        })
    )


# 👤 FORMULARIO PACIENTE
class ResidenteForm(forms.ModelForm):
    class Meta:
        model = Residente
        fields = ['rut', 'nombre', 'apellido', 'habitacion_numero', 'alertas_criticas']

        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678-9'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'habitacion_numero': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'alertas_criticas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ej: Alergia a penicilina'
            }),
        }