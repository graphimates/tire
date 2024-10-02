# averias/forms.py
from django import forms
from .models import Averia

class AveriaForm(forms.ModelForm):
    class Meta:
        model = Averia
        fields = ['nombre', 'codigo', 'servicio_requerido']  # Incluimos el campo código
        labels = {
            'nombre': 'Nombre de la Avería',
            'codigo': 'Código de la Avería',
            'servicio_requerido': 'Servicio Requerido',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio_requerido': forms.Select(attrs={'class': 'form-control'}),
        }
