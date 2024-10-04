from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UsuarioForm
from django.views.decorators.cache import never_cache
from .forms import ModificarImagenForm, ProfileForm
from averias.models import Averia
import csv
from django.http import HttpResponse
from neumatico.models import Neumatico, HistorialInspeccion
from vehiculos.models import Vehiculo
from django.db.models import Q  # Importamos Q para hacer búsquedas complejas


# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser


# Vista para mostrar los usuarios en una tabla con búsqueda por empresa
@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def ver_usuarios(request):
    # Obtener el término de búsqueda de la empresa
    search_query = request.GET.get('search_empresa', '')

    # Filtrar los usuarios según el término de búsqueda en la empresa
    if search_query:
        usuarios = Usuario.objects.filter(Q(empresa__icontains=search_query))
    else:
        usuarios = Usuario.objects.all()  # Mostrar todos los usuarios si no hay búsqueda

    return render(request, 'usuarios/ver_usuarios.html', {
        'usuarios': usuarios,
        'search_query': search_query,  # Pasamos el término de búsqueda a la plantilla
    })


@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        usuario.delete()  # Eliminar el usuario
        return redirect('ver_usuarios')  # Redirigir de nuevo a la lista de usuarios
    return render(request, 'usuarios/eliminar_confirmacion.html', {'usuario': usuario})


@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)  # Agregar request.FILES
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])  # Encriptar la contraseña
            usuario.save()
            return redirect('ver_usuarios')  # Redirigir a la lista de usuarios después de la creación
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})


@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)  # Obtener el usuario por ID
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)  # Cargar el formulario con los datos existentes
        if form.is_valid():
            form.save()
            return redirect('ver_usuarios')  # Redirigir a la lista de usuarios después de la edición
    else:
        form = UsuarioForm(instance=usuario)  # Precargar el formulario con los datos del usuario
    return render(request, 'usuarios/crear_usuario.html', {'form': form, 'titulo': f'Editando al usuario {usuario.first_name}'})


@never_cache  # Deshabilitar la caché
@login_required
def modificar_imagen(request):
    if request.method == 'POST':
        form = ModificarImagenForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')  # Redirige a una página de perfil o donde prefieras
    else:
        form = ModificarImagenForm(instance=request.user)
    return render(request, 'usuarios/modificar_imagen.html', {'form': form})


@never_cache  # Deshabilitar la caché
@login_required
def perfil_usuario(request):
    usuario = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = ProfileForm(instance=usuario)
    return render(request, 'usuarios/perfil_usuario.html', {'form': form})


@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
def ver_averias(request):
    averias = Averia.objects.all()
    return render(request, 'averias/ver_averias.html', {'averias': averias})


@login_required
@user_passes_test(is_admin)
def descargar_informacion_usuario(request, user_id):
    # Obtener el usuario seleccionado por el administrador
    usuario = get_object_or_404(Usuario, id=user_id)
    
    # Obtener los vehículos del usuario seleccionado
    vehiculos = Vehiculo.objects.filter(usuario=usuario)
    
    # Crear una respuesta HTTP con el archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{usuario.first_name}_{usuario.last_name}_inspecciones.csv"'
    
    writer = csv.writer(response)
    
    # Escribir el encabezado del CSV
    writer.writerow(['Placa Vehículo', 'Posición Neumático', 'Modelo', 'Marca', 'DOT', 'Presión', 'Huella', 'Fecha de Inspección', 'Averías', 'Renovable'])
    
    # Escribir la información de la última inspección de cada neumático (NO en el historial)
    for vehiculo in vehiculos:
        neumaticos = Neumatico.objects.filter(vehiculo=vehiculo)
        for neumatico in neumaticos:
            averias = ', '.join([averia.nombre for averia in neumatico.averias.all()]) or 'Sin averías'
            writer.writerow([
                vehiculo.placa,
                neumatico.posicion,
                neumatico.modelo,
                neumatico.marca,
                neumatico.dot,
                neumatico.presion,
                neumatico.huella,
                neumatico.fecha_inspeccion,
                averias,
                'Sí' if neumatico.renovable else 'No'
            ])
    
    # Escribir el historial de inspecciones del usuario
    historial_inspecciones = HistorialInspeccion.objects.filter(vehiculo__usuario=usuario).order_by('-fecha_inspeccion')
    for inspeccion in historial_inspecciones:
        averia_nombre = inspeccion.averia.nombre if inspeccion.averia else 'Sin averías'
        writer.writerow([
            inspeccion.vehiculo.placa,
            inspeccion.posicion,
            inspeccion.modelo,
            inspeccion.marca,
            inspeccion.dot,
            inspeccion.presion,
            inspeccion.huella,
            inspeccion.fecha_inspeccion,
            averia_nombre,
            'Sí' if inspeccion.renovable else 'No'
        ])
    
    return response
