from django import forms
from .models import Neumatico, MedidaNeumatico

class NeumaticoForm(forms.ModelForm):
    class Meta:
        model = Neumatico
        fields = ['modelo', 'medida', 'marca', 'diseño', 'dot', 'presion', 'huella', 'averias', 'renovable']
        widgets = {
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),  # Campo de modelo
            'medida': forms.Select(attrs={'class': 'form-control'}),
            'diseño': forms.TextInput(attrs={'class': 'form-control'}),
            'averias': forms.CheckboxSelectMultiple(),
            'renovable': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super(NeumaticoForm, self).__init__(*args, **kwargs)
        self.fields['averias'].required = False
        self.fields['renovable'].initial = False  # No marcar por defecto 'renovable'


class MedidaForm(forms.ModelForm):
    class Meta:
        model = MedidaNeumatico
        fields = ['medida', 'precio_estimado']
        labels = {
            'medida': 'Medida del Neumático',
            'precio_estimado': 'Precio Estimado',
        }
        widgets = {
            'medida': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_estimado': forms.NumberInput(attrs={'class': 'form-control'}),
        }