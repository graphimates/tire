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

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('first_name'):
            self.add_error('first_name', 'El nombre es obligatorio.')
        if not cleaned_data.get('last_name'):
            self.add_error('last_name', 'El apellido es obligatorio.')
        if not cleaned_data.get('email'):
            self.add_error('email', 'El correo electrónico es obligatorio.')
        if not cleaned_data.get('empresa'):
            self.add_error('empresa', 'La empresa es obligatoria.')
        if not cleaned_data.get('password'):
            self.add_error('password', 'La contraseña es obligatoria.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['profile_photo']