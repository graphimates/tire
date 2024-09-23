# usuarios/models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, empresa, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, empresa=empresa, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, empresa, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, first_name, last_name, empresa, password, **extra_fields)

class Usuario(AbstractUser):
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    username = None  # Desactivamos el campo username
    email = models.EmailField(unique=True)
    empresa = models.CharField(max_length=100)
    flota = models.IntegerField(default=0)  # Cantidad de vehículos (flota) del usuario
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        default='default-profile.png',
        blank=True,
        null=True  # Aseguramos que el campo puede ser nulo
    )
    
    USERNAME_FIELD = 'email'  # Usamos el correo electrónico como identificador único
    REQUIRED_FIELDS = ['first_name', 'last_name', 'empresa']  # Campos requeridos adicionales

    objects = UsuarioManager()  # Manager personalizado para el modelo

    def get_full_name(self):
        """Devuelve el nombre completo del usuario."""
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        """Devuelve una representación del usuario con el correo."""
        return self.email

