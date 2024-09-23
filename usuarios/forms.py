from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña",
        required=True
    )
    is_superuser = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        label="¿Es administrador?",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'empresa', 'password', 'is_superuser', 'profile_photo']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'empresa': 'Empresa',
            'is_superuser': '¿Es administrador?',
            'profile_photo': 'Foto de Perfil',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

# Formulario para editar la imagen de perfil
class ModificarImagenForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['profile_photo']
        labels = {
            'profile_photo': 'Foto de Perfil',
        }
        widgets = {
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

# Formulario para editar la imagen de perfil usuarios
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['profile_photo']  # Solo este campo está presente en ProfileForm

    # Elimina las validaciones de los campos que no están en este formulario
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('profile_photo'):
            self.add_error('profile_photo', 'La foto de perfil es obligatoria.')
        return cleaned_data

    # Si no hay contraseña en este formulario, elimina el método save relacionado con contraseñas



    # Si no hay contraseña en este formulario, elimina el método save relacionado con contraseñas


