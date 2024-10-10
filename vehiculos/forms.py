# vehiculos/forms.py

from django import forms
from .models import Vehiculo

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['placa', 'modelo', 'tipo']
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

    def clean_placa(self):
        placa = self.cleaned_data.get('placa')
        if Vehiculo.objects.filter(placa=placa).exists():
            raise forms.ValidationError("Ya existe un vehículo con esta placa.")
        return placa
