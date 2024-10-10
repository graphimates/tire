# neumatico/forms.py
from django import forms
from .models import Neumatico, MedidaNeumatico

class NeumaticoForm(forms.ModelForm):
    class Meta:
        model = Neumatico
        fields = ['modelo', 'marca', 'medida', 'presion', 'huella', 'dot', 'averias', 'diseño', 'renovable']
        widgets = {
            'modelo': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'medida': forms.Select(attrs={'class': 'form-control'}),
            'presion': forms.NumberInput(attrs={'class': 'form-control'}),
            'huella': forms.NumberInput(attrs={'class': 'form-control'}),
            'dot': forms.TextInput(attrs={'class': 'form-control'}),
            'averias': forms.CheckboxSelectMultiple(),
            'diseño': forms.TextInput(attrs={'class': 'form-control'}),
            'renovable': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super(NeumaticoForm, self).__init__(*args, **kwargs)
        self.fields['averias'].required = False
        self.fields['renovable'].initial = False
        self.fields['dot'].required = True

    def clean(self):
        cleaned_data = super().clean()
        renovable = cleaned_data.get('renovable')
        averias = cleaned_data.get('averias')
        

        if averias:
            if any(averia.estado == 'no_operativo' for averia in averias):
                if renovable:
                    self.add_error('renovable', 'El neumático no puede ser renovable si tiene una avería no operativa.')
                cleaned_data['renovable'] = False

        return cleaned_data
    

    


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