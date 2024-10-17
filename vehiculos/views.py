from django.shortcuts import render, get_object_or_404, redirect
from .models import Vehiculo
from usuarios.models import Usuario
from .forms import VehiculoForm
from neumatico.models import Neumatico 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache  # Importamos el decorador para deshabilitar la caché
import json  # Asegúrate de importar json
from django.contrib import messages  # Importar para mostrar mensajes al usuario

# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

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

            try:
                # Crear los neumáticos relacionados
                for posicion in range(1, vehiculo.cantidad_neumaticos + 1):
                    Neumatico.objects.create(
                        vehiculo=vehiculo,
                        posicion=posicion,
                        modelo='',
                        marca='',
                        diseño='',
                        dot='',
                        presion=None,  # No asignar presión
                        huella=None,   # No asignar huella
                        renovable=False,  # No es renovable inicialmente
                        averias=None  # No asignar averías
                    )
            except Exception as e:
                # Capturar el error y redirigir o mostrar un mensaje
                messages.error(request, "Ocurrió un error al crear los neumáticos, pero el vehículo fue creado exitosamente.")
                # Puedes redirigir a otra URL si lo prefieres
                return redirect('ver_usuarios')

            # Actualizar la flota del usuario
            usuario.flota += 1
            usuario.save()

            return redirect('ver_usuarios')
    else:
        form = VehiculoForm()

    return render(request, 'vehiculos/crear_vehiculo.html', {'form': form, 'usuario': usuario})
from django.core.paginator import Paginator

@login_required
@never_cache
def reporte_vehiculos(request):
    vehiculos_con_neumaticos = []

    # Obtener los valores de los filtros desde el formulario GET
    selected_empresa = request.GET.get('selected_empresa', '')
    order_by = request.GET.get('order_by', 'desc')
    criticidad = request.GET.get('criticidad', '')

    # Si el usuario es superusuario, obtener la lista de empresas
    if request.user.is_superuser:
        empresas = Usuario.objects.values_list('empresa', flat=True).distinct()
        vehiculos = Vehiculo.objects.all()

        # Si hay una empresa seleccionada, filtrar los vehículos por empresa
        if selected_empresa and selected_empresa != 'todas':
            vehiculos = vehiculos.filter(usuario__empresa__iexact=selected_empresa)

        if criticidad:
            vehiculos = vehiculos.filter(neumaticos__averias__criticidad=criticidad).distinct()

    else:
        vehiculos = Vehiculo.objects.filter(usuario=request.user)
        empresas = []  # No mostrar la lista de empresas si no es superusuario

    # Ordenar los vehículos por fecha de inspección
    if order_by == 'asc':
        vehiculos = vehiculos.order_by('ultima_inspeccion')
    else:
        vehiculos = vehiculos.order_by('-ultima_inspeccion')

    # Paginación - mostrar 8 vehículos por página
    paginator = Paginator(vehiculos, 8)  # 8 vehículos por página
    page_number = request.GET.get('page')  # Número de la página actual
    page_obj = paginator.get_page(page_number)  # Obtener la página actual

    # Recorrer los vehículos en la página actual y preparar el contexto
    for vehiculo in page_obj:
        neumaticos_por_posicion = {}
        tiene_averias = False

        for i in range(1, vehiculo.cantidad_neumaticos + 1):
            neumatico = vehiculo.neumaticos.filter(posicion=i).first()
            neumaticos_por_posicion[i] = neumatico

            # Verificar si algún neumático tiene averías
            if neumatico and neumatico.averias.exists():
                tiene_averias = True

        vehiculos_con_neumaticos.append({
            'vehiculo': vehiculo,
            'neumaticos_por_posicion': neumaticos_por_posicion,
            'rango_posiciones': range(1, vehiculo.cantidad_neumaticos + 1),
            'tiene_averias': tiene_averias  # Añadir la variable tiene_averias
        })

    # Asegurarse de pasar 'selected_empresa', 'page_obj' y empresas al contexto
    return render(request, 'vehiculos/reporte_vehiculos.html', {
        'vehiculos_con_neumaticos': vehiculos_con_neumaticos,
        'empresas': empresas,
        'selected_empresa': selected_empresa,
        'page_obj': page_obj,  # Pasar el objeto de paginación al template
    })



@never_cache
@login_required
@user_passes_test(is_admin)
def borrar_vehiculo(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    vehiculo.delete()
    return redirect('reporte_vehiculos')

@login_required
@user_passes_test(is_admin)
def editar_fecha_inspeccion(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)

    if request.method == 'POST':
        nueva_fecha = request.POST.get('fecha_inspeccion')
        if nueva_fecha:
            # Actualizar la fecha de inspección de todos los neumáticos actuales
            vehiculo.ultima_inspeccion = nueva_fecha
            vehiculo.neumaticos.update(fecha_inspeccion=nueva_fecha)  # Actualizar los neumáticos actuales
            vehiculo.save()
            return redirect('reporte_vehiculos')

    return redirect('reporte_vehiculos')
