from django.shortcuts import render, get_object_or_404, redirect
from .models import Vehiculo
from usuarios.models import Usuario
from .forms import VehiculoForm
from django.contrib.auth.decorators import login_required, user_passes_test

# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

# Vista para añadir un vehículo a un usuario específico
@login_required
@user_passes_test(is_admin)
def crear_vehiculo(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.usuario = usuario
            vehiculo.save()
            # Actualizar la flota
            usuario.flota += 1
            usuario.save()
            return redirect('ver_usuarios')
    else:
        form = VehiculoForm()
    
    return render(request, 'vehiculos/crear_vehiculo.html', {'form': form, 'usuario': usuario})
