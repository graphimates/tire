from django.shortcuts import render, get_object_or_404, redirect
from .models import Averia
from .forms import AveriaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache

# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

# Vista para mostrar las averías en una tabla
@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def ver_averias(request):
    averias = Averia.objects.all()  # Obtener todas las averías
    return render(request, 'averias/ver_averias.html', {'averias': averias})

@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def eliminar_averia(request, averia_id):
    averia = get_object_or_404(Averia, id=averia_id)
    if request.method == 'POST':
        averia.delete()  # Eliminar la avería
        return redirect('ver_averias')  # Redirigir de nuevo a la lista de averías
    return render(request, 'averias/eliminar_confirmacion.html', {'averia': averia})

@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def crear_averia(request):
    if request.method == 'POST':
        form = AveriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_averias')  # Redirigir a la lista de averías después de la creación
    else:
        form = AveriaForm()
    return render(request, 'averias/crear_averia.html', {'form': form, 'titulo': 'Crear Avería'})

@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def editar_averia(request, averia_id):
    averia = get_object_or_404(Averia, id=averia_id)  # Obtener la avería por ID
    if request.method == 'POST':
        form = AveriaForm(request.POST, instance=averia)  # Cargar el formulario con los datos existentes
        if form.is_valid():
            form.save()
            return redirect('ver_averias')  # Redirigir a la lista de averías después de la edición
    else:
        form = AveriaForm(instance=averia)  # Precargar el formulario con los datos de la avería
    return render(request, 'averias/crear_averia.html', {'form': form, 'titulo': f'Editando la avería {averia.nombre}'})
