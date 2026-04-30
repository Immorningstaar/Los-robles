from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Residente, PlanMedicacion


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
        # Agregamos los 3 campos nuevos al final de esta lista
        fields = ['rut', 'nombre', 'apellido', 'habitacion_numero', 'alertas_criticas', 
                  'diagnostico_principal', 'contacto_familiar', 'condicion_deglucion']
    class Meta:
        model = Residente
        # Agregamos los 3 campos nuevos al final de esta lista
        fields = ['rut', 'nombre', 'apellido', 'habitacion_numero', 'alertas_criticas', 
                  'diagnostico_principal', 'contacto_familiar', 'condicion_deglucion']

        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'habitacion_numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'alertas_criticas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej: Alergia a penicilina'}),
            
            # 🔥 NUESTROS 3 CAMPOS CON DISEÑO BOOTSTRAP
            'diagnostico_principal': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Hipertensión, Diabetes...'
            }),
            'contacto_familiar': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre y Teléfono'
            }),
            'condicion_deglucion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Normal, Molido, Sonda'
            }),
        }

# 💊 FORMULARIO ASIGNAR PLAN (RECUPERADO)
class PlanMedicacionForm(forms.ModelForm):
    class Meta:
        model = PlanMedicacion
        fields = '__all__'
        # Esto hace que en el HTML aparezcan los selectores de fecha y hora de Bootstrap/Navegador
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fecha_inicio_plan': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }