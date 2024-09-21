from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    # Campo de contraseña opcional para que no sea obligatorio en la edición
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña (déjelo vacío si no desea cambiarla)",
        required=False  # La contraseña es opcional en la edición
    )
    is_superuser = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        label="¿Es administrador?",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'empresa', 'password', 'is_superuser']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'empresa': 'Empresa',
            'is_superuser': '¿Es administrador?',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        # Si se ha ingresado una nueva contraseña, la actualizamos
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Actualiza la contraseña solo si se proporciona una nueva
        else:
            # Si no se proporciona una nueva contraseña, mantenemos la actual
            user.password = Usuario.objects.get(pk=user.pk).password

        if commit:
            user.save()
        return user
