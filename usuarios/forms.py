from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña",
        required=False  # La contraseña es opcional en la edición
    )
    is_superuser = forms.ChoiceField(
        choices=[(False, 'No'), (True, 'Sí')],  # Cambié el orden para que "No" esté primero
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

    def save(self, commit=True):
        user = super().save(commit=False)

        # Si se ha ingresado una nueva contraseña, la actualizamos
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Actualiza la contraseña solo si se proporciona una nueva
        else:
            # Si no se proporciona una nueva contraseña, mantenemos la actual
            if user.pk:  # Verificamos si el usuario ya existe
                user.password = Usuario.objects.get(pk=user.pk).password

        if commit:
            user.save()
        return user

# Formulario para modificar la imagen de perfil
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

# Formulario para modificar solo la imagen de perfil
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['profile_photo']

    # No es necesario el método `clean` aquí, ya que Django manejará la validación automáticamente

