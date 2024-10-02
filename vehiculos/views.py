from django.shortcuts import render, get_object_or_404, redirect
from .models import Vehiculo
from usuarios.models import Usuario
from .forms import VehiculoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache  # Importamos el decorador para deshabilitar la caché

# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

# Vista para añadir un vehículo a un usuario específico
@never_cache  # Deshabilitar la caché
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

# Vista para el reporte de vehículos
@never_cache
@login_required
def reporte_vehiculos(request):
    if request.user.is_superuser:
        vehiculos = Vehiculo.objects.select_related('usuario').prefetch_related('neumaticos').all()
    else:
        vehiculos = Vehiculo.objects.filter(usuario=request.user).prefetch_related('neumaticos')

    # Preparar los neumáticos con su posición y avería
    vehiculos_con_neumaticos = []
    for vehiculo in vehiculos:
        neumaticos = vehiculo.neumaticos.order_by('posicion')
        neumaticos_por_posicion = {neumatico.posicion: neumatico for neumatico in neumaticos}
        vehiculos_con_neumaticos.append({
            'vehiculo': vehiculo,
            'neumaticos_por_posicion': neumaticos_por_posicion
        })

    return render(request, 'vehiculos/reporte_vehiculos.html', {'vehiculos_con_neumaticos': vehiculos_con_neumaticos})


@never_cache
@login_required
@user_passes_test(is_admin)
def borrar_vehiculo(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)

    # Eliminar el vehículo (los neumáticos asociados se eliminarán automáticamente por la relación on_delete)
    vehiculo.delete()

    return redirect('reporte_vehiculos')
