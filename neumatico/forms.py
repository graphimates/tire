from django import forms
from .models import Neumatico
from averias.models import Averia

class NeumaticoForm(forms.ModelForm):
    class Meta:
        model = Neumatico
        fields = ['posicion', 'modelo', 'marca', 'dot', 'presion', 'huella', 'averias']
        widgets = {
            'posicion': forms.HiddenInput(),
            'averias': forms.CheckboxSelectMultiple(),  # Permitir seleccionar varias averías
        }
