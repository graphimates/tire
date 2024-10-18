# wheels/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from neumatico.models import Neumatico, HistorialInspeccion  # Asegúrate de importar HistorialInspeccion si lo necesitas
from usuarios.models import Usuario
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from averias.models import Averia
import json
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from vehiculos.models import Vehiculo
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max  # Importar Max para agregaciones

# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

# Vista para el login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    form = AuthenticationForm(request, data=request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            email = request.POST.get('username')  # AuthenticationForm usa 'username' para el campo de email
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, 'Credenciales incorrectas.')
    
    return render(request, 'login.html', {'form': form})

# Vista para el index (admin panel)
@login_required
@never_cache
def index(request):
    # Inicializar selected_empresa con un valor por defecto
    selected_empresa = None

    # Verificar si el usuario es superusuario
    if not request.user.is_superuser:
        # Si no es superusuario, solo mostrar sus propios datos
        selected_user = request.user
        usuarios_filtrados = Usuario.objects.filter(id=request.user.id)
    else:
        # Si es superusuario, proceder con las opciones de filtrado
        search_empresa = request.GET.get('search_empresa', '')
        selected_empresa = request.GET.get('selected_empresa', '')

        if selected_empresa == 'todas':
            usuarios_filtrados = Usuario.objects.exclude(is_superuser=True)
            selected_user = None  # No hay un usuario específico seleccionado
        elif selected_empresa:
            usuarios_filtrados = Usuario.objects.filter(empresa__iexact=selected_empresa).exclude(is_superuser=True)
            selected_user = usuarios_filtrados.first() if usuarios_filtrados.exists() else None
        elif search_empresa:
            usuarios_filtrados = Usuario.objects.filter(empresa__icontains=search_empresa).exclude(is_superuser=True)
            selected_user = usuarios_filtrados.first() if usuarios_filtrados.exists() else None
        else:
            usuarios_filtrados = Usuario.objects.exclude(is_superuser=True)
            selected_user = None

    # Obtener los neumáticos según el usuario seleccionado o filtrado
    if selected_user:
        neumaticos = Neumatico.objects.filter(vehiculo__usuario=selected_user).select_related('vehiculo__usuario').prefetch_related('averias')
    else:
        neumaticos = Neumatico.objects.filter(vehiculo__usuario__in=usuarios_filtrados).select_related('vehiculo__usuario').prefetch_related('averias')

    # Inicializar contadores y listas
    total_neumaticos = 0
    operativos_count = 0
    no_operativos_count = 0
    huella_0_3 = 0
    huella_3_6 = 0
    huella_6_mas = 0

    # Listas para almacenar neumáticos operativos y no operativos
    neumaticos_operativos = []
    neumaticos_no_operativos = []

    # Inicializar el contador de servicios por vehículo
    servicios_por_vehiculo = {
        'alineacion': set(),  # Usaremos sets para evitar contar el mismo vehículo varias veces
        'balanceo': set(),
        'rotacion': set(),
        'montura': set(),
        'calibracion': set(),
    }

    # Recorrer todos los neumáticos seleccionados
    for neumatico in neumaticos:
        total_neumaticos += 1

        # Verificar si tiene una avería de estado 'no_operativo'
        tiene_averia_no_operativo = neumatico.averias.filter(estado='no_operativo').exists()

        # Sumar cada servicio requerido por las averías a nivel de vehículo
        for averia in neumatico.averias.all():
            if averia.servicio_requerido in servicios_por_vehiculo:
                servicios_por_vehiculo[averia.servicio_requerido].add(neumatico.vehiculo.placa)

        # Es operativo si no tiene una avería no operativa, independientemente de la huella
        if not tiene_averia_no_operativo:
            operativos_count += 1
            neumaticos_operativos.append(neumatico)

            # Clasificar la huella del neumático si es operativo
            if neumatico.huella <= 3:
                huella_0_3 += 1
            elif 3 < neumatico.huella <= 6:
                huella_3_6 += 1
            elif neumatico.huella > 6:
                huella_6_mas += 1
        else:
            # Es no operativo solo si tiene una avería no operativa
            no_operativos_count += 1
            neumaticos_no_operativos.append(neumatico)

    # Convertir los sets de placas a listas
    servicios_por_vehiculo_list = {servicio: list(placas) for servicio, placas in servicios_por_vehiculo.items()}

    # Obtener todas las empresas para el autocompletado y la lista desplegable (solo para superusuarios)
    empresas = Usuario.objects.values_list('empresa', flat=True).distinct().exclude(is_superuser=True) if request.user.is_superuser else []
    empresas_json = json.dumps(list(empresas))  # Convertir a JSON para el autocompletar

    # Calcular la última inspección y el conteo de flota
    if not request.user.is_superuser:
        # Para usuarios no administradores, obtener la última inspección de sus neumáticos actuales
        ultima_inspeccion = Neumatico.objects.filter(vehiculo__usuario=request.user, fecha_inspeccion__isnull=False).order_by('-fecha_inspeccion').first()
        # Calcular el conteo de flota (vehículos) del usuario
        fleet_count = Vehiculo.objects.filter(usuario=request.user).count()
    else:
        # Para administradores, determinar la última inspección según la selección
        if selected_empresa and selected_empresa != 'todas':
            usuarios_empresa = Usuario.objects.filter(empresa__iexact=selected_empresa).exclude(is_superuser=True)
            # Obtener la última inspección de los neumáticos actuales de los usuarios de la empresa seleccionada
            ultima_inspeccion = Neumatico.objects.filter(vehiculo__usuario__in=usuarios_empresa, fecha_inspeccion__isnull=False).order_by('-fecha_inspeccion').first()
            # Calcular el conteo de flota de la empresa seleccionada
            fleet_count = Vehiculo.objects.filter(usuario__in=usuarios_empresa).count()
        elif selected_empresa == 'todas':
            # Obtener la última inspección de todos los neumáticos actuales
            ultima_inspeccion = Neumatico.objects.filter(fecha_inspeccion__isnull=False).order_by('-fecha_inspeccion').first()
            # Calcular el conteo total de flota
            fleet_count = Vehiculo.objects.all().count()
        else:
            # Si no se ha seleccionado ninguna empresa, opta por la última inspección general de neumáticos actuales
            ultima_inspeccion = Neumatico.objects.filter(fecha_inspeccion__isnull=False).order_by('-fecha_inspeccion').first()
            # Calcular el conteo total de flota
            fleet_count = Vehiculo.objects.all().count()

    # Preparar el contexto para la vista
    context = {
        'total_neumaticos': total_neumaticos,
        'operativos': operativos_count,
        'no_operativos': no_operativos_count,
        'huella_0_3': huella_0_3,
        'huella_3_6': huella_3_6,
        'huella_6_mas': huella_6_mas,
        'servicios_por_vehiculo': servicios_por_vehiculo_list,  # Pasar listas de placas
        'usuarios': usuarios_filtrados,
        'selected_user': selected_user,
        'empresas': empresas,
        'empresas_json': empresas_json,
        'selected_empresa': selected_empresa,
        'neumaticos_operativos': neumaticos_operativos,
        'neumaticos_no_operativos': neumaticos_no_operativos,
        'ultima_inspeccion': ultima_inspeccion,  # Agregar la última inspección al contexto
        'fleet_count': fleet_count,  # Agregar el conteo de flota al contexto
    }

    return render(request, 'index.html', context)

# Vista para autocompletar empresas
@login_required
def autocomplete_empresas(request):
    if request.is_ajax():
        term = request.GET.get('term', '')
        empresas = Usuario.objects.filter(empresa__icontains=term).exclude(is_superuser=True).values_list('empresa', flat=True).distinct()
        empresas_list = list(empresas)
        return JsonResponse(empresas_list, safe=False)

@login_required
def empresa_autocomplete(request):
    if request.is_ajax():
        query = request.GET.get('term', '')  # Obtén el término que está buscando el usuario
        # Filtra las empresas que coinciden con el término
        empresas = Usuario.objects.filter(empresa__icontains=query).exclude(is_superuser=True).values_list('empresa', flat=True).distinct()
        results = list(empresas)
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)
