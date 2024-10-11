from django.shortcuts import render, get_object_or_404, redirect
from .models import Vehiculo
from usuarios.models import Usuario
from .forms import VehiculoForm
from neumatico.models import Neumatico 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache  # Importamos el decorador para deshabilitar la caché
import json  # Asegúrate de importar json

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
            
            # Ahora, crear los neumáticos relacionados
            for posicion in range(1, vehiculo.cantidad_neumaticos + 1):
                Neumatico.objects.create(
                    vehiculo=vehiculo,
                    posicion=posicion,
                    modelo='',
                    marca='',
                    diseño='',
                    dot='',
                    presion=0.0,
                    huella=0.0,
                    renovable=False
                )
            
            # Actualizar la flota
            usuario.flota += 1
            usuario.save()
            return redirect('ver_usuarios')
    else:
        form = VehiculoForm()
    
    return render(request, 'vehiculos/crear_vehiculo.html', {'form': form, 'usuario': usuario})

@login_required
@never_cache
def reporte_vehiculos(request):
    vehiculos_con_neumaticos = []

    # Filtrar por empresa
    search_empresa = request.GET.get('search_empresa', '')
    order_by = request.GET.get('order_by', 'desc')
    criticidad = request.GET.get('criticidad', '')

    if request.user.is_superuser:
        empresas = Usuario.objects.values_list('empresa', flat=True).distinct()
        vehiculos = Vehiculo.objects.all()

        if search_empresa:
            vehiculos = vehiculos.filter(usuario__empresa__icontains=search_empresa)

        if criticidad:
            vehiculos = vehiculos.filter(neumaticos__averias__criticidad=criticidad).distinct()

    else:
        vehiculos = Vehiculo.objects.filter(usuario=request.user)
        empresas = []

    # Ordenar los vehículos por fecha de inspección
    if order_by == 'asc':
        vehiculos = vehiculos.order_by('ultima_inspeccion')
    else:
        vehiculos = vehiculos.order_by('-ultima_inspeccion')

    for vehiculo in vehiculos:
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

    return render(request, 'vehiculos/reporte_vehiculos.html', {
        'vehiculos_con_neumaticos': vehiculos_con_neumaticos,
        'empresas_json': json.dumps(list(empresas)),
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
