from django import forms
from .models import Vehiculo

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['placa', 'modelo', 'tipo']  # Elimina 'marca'
        labels = {
            'placa': 'Placa',
            'modelo': 'Modelo',
            'tipo': 'Tipo de Vehículo',
        }
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }
