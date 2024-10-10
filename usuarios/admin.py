from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    ordering = ['email']  # Cambiamos el orden por 'email'
    list_display = ['email', 'first_name', 'last_name', 'empresa', 'is_superuser']
    search_fields = ['email', 'first_name', 'last_name']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'empresa')}),
        ('Permisos', {'fields': ('is_superuser', 'is_staff', 'is_active')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'empresa', 'password1', 'password2', 'is_superuser'),
        }),
    )

admin.site.register(Usuario, UsuarioAdmin)
