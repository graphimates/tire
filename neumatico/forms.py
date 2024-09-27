# forms.py
from django import forms
from .models import Neumatico
from averias.models import Averia

class NeumaticoForm(forms.ModelForm):
    class Meta:
        model = Neumatico
        fields = ['posicion', 'modelo', 'marca', 'dot', 'presion', 'huella', 'averias']
        widgets = {
            'posicion': forms.HiddenInput(),
            'averias': forms.CheckboxSelectMultiple(),
        }

    # Marcar el campo averias como no requerido
    def __init__(self, *args, **kwargs):
        super(NeumaticoForm, self).__init__(*args, **kwargs)
        self.fields['averias'].required = False
