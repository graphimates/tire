from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UsuarioForm
from django.views.decorators.cache import never_cache
from .forms import ModificarImagenForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from averias.models import Averia
import csv
from django.http import HttpResponse
from neumatico.models import Neumatico, HistorialInspeccion
from vehiculos.models import Vehiculo


# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

# Vista para mostrar los usuarios en una tabla
@login_required
@user_passes_test(is_admin)
@never_cache
def ver_usuarios(request):
    usuarios = Usuario.objects.all()  # Obtener todos los usuarios
    return render(request, 'usuarios/ver_usuarios.html', {'usuarios': usuarios})


@login_required
@user_passes_test(is_admin)
@never_cache
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        usuario.delete()
        return redirect('ver_usuarios')
    return render(request, 'usuarios/eliminar_confirmacion.html', {'usuario': usuario})

# Vista para el registro de usuario
@login_required
@user_passes_test(is_admin)
@never_cache
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)  # Agregar request.FILES para cargar archivos
        if form.is_valid():
            empresa = form.cleaned_data.get('empresa')
            if Usuario.objects.filter(empresa=empresa).exists():
                form.add_error('empresa', 'El nombre de la empresa ya está registrado. Por favor, elija un nombre diferente.')
            else:
                usuario = form.save(commit=False)
                usuario.set_password(form.cleaned_data['password'])  # Encriptar la contraseña
                
                # Verificar si no se subió una imagen y asignar una por defecto
                if not usuario.profile_photo:
                    usuario.profile_photo = 'profile_photos/default-profile.png'  # Imagen por defecto
                
                usuario.save()
                return redirect('ver_usuarios')  # Redirigir a la lista de usuarios después de la creación
    else:
        form = UsuarioForm()
    
    return render(request, 'usuarios/crear_usuario.html', {'form': form})


@login_required
@user_passes_test(is_admin)
@never_cache
def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('ver_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/crear_usuario.html', {'form': form, 'titulo': f'Editando al usuario {usuario.first_name}'})

@never_cache
@login_required
def modificar_imagen(request):
    if request.method == 'POST':
        form = ModificarImagenForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = ModificarImagenForm(instance=request.user)
    return render(request, 'usuarios/modificar_imagen.html', {'form': form})


@never_cache
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
@user_passes_test(is_admin)
def ver_averias(request):
    averias = Averia.objects.all()
    return render(request, 'averias/ver_averias.html', {'averias': averias})


@login_required
@user_passes_test(is_admin)
def descargar_informacion_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    vehiculos = Vehiculo.objects.filter(usuario=usuario)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{usuario.first_name}_{usuario.last_name}_inspecciones.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Placa Vehículo', 'Posición Neumático', 'Modelo', 'Marca', 'DOT', 'Presión', 'Huella', 'Fecha de Inspección', 'Averías', 'Renovable'])
    
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
