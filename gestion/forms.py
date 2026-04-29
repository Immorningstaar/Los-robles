from django import forms
from .models import Residente, PlanMedicacion

class ResidenteForm(forms.ModelForm):
    class Meta:
        model = Residente
        fields = '__all__'

class PlanMedicacionForm(forms.ModelForm):
    class Meta:
        model = PlanMedicacion
        fields = '__all__'
        # Esto hace que en el HTML aparezcan los selectores de fecha y hora de Bootstrap/Navegador
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fecha_inicio_plan': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }