from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'empresa']

admin.site.register(Usuario, UsuarioAdmin)
