# averias/forms.py
from django import forms
from .models import Averia

# averias/forms.py
class AveriaForm(forms.ModelForm):
    class Meta:
        model = Averia
        fields = ['nombre', 'codigo', 'servicio_requerido', 'estado']
        labels = {
            'nombre': 'Nombre de la Avería',
            'codigo': 'Código de la Avería',
            'servicio_requerido': 'Servicio Requerido',
            'estado': 'Estado de la Avería',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio_requerido': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AveriaForm, self).__init__(*args, **kwargs)
        self.fields['estado'].initial = 'no_operativo'  # Establecer el valor por defecto en el formulario
