from django import forms
from .models import Averia

class AveriaForm(forms.ModelForm):
    class Meta:
        model = Averia
        fields = ['nombre', 'estado_neumatico', 'descripcion']
        labels = {
            'nombre': 'Nombre de la Avería',
            'estado_neumatico': 'Estado del Neumático',
            'descripcion': 'Descripción de la Avería',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_neumatico': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
