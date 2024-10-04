from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from neumatico.models import Neumatico
from usuarios.models import Usuario
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from averias.models import Averia
import json
from django.http import JsonResponse
from django.db.models import Q


# Vista para el login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('index')
            else:
                return redirect('user_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas.'})
    
    return render(request, 'login.html')


# Vista para el index (admin panel)
@login_required
@never_cache
def index(request):
    # Obtener el término de búsqueda y el filtro seleccionado
    search_empresa = request.GET.get('search_empresa', '')
    selected_empresa = request.GET.get('selected_empresa', '')

    # Verificar si se seleccionó "Todas las empresas"
    if selected_empresa == 'todas':
        usuarios_filtrados = Usuario.objects.exclude(is_superuser=True)
        selected_user = None  # No hay un usuario específico seleccionado
    elif selected_empresa:
        # Si hay una empresa seleccionada, filtrar por ella
        usuarios_filtrados = Usuario.objects.filter(empresa__iexact=selected_empresa).exclude(is_superuser=True)
        selected_user = usuarios_filtrados.first() if usuarios_filtrados.exists() else None
    elif search_empresa:
        # Búsqueda manual por empresa
        usuarios_filtrados = Usuario.objects.filter(empresa__icontains=search_empresa).exclude(is_superuser=True)
        selected_user = usuarios_filtrados.first() if usuarios_filtrados.exists() else None
    else:
        # Si no hay filtro, mostrar todos los usuarios (menos los admins)
        usuarios_filtrados = Usuario.objects.exclude(is_superuser=True)
        selected_user = None

    # Obtener los neumáticos de todos los usuarios o de un usuario específico
    if selected_user:
        neumaticos = Neumatico.objects.filter(vehiculo__usuario=selected_user)
    else:
        neumaticos = Neumatico.objects.filter(vehiculo__usuario__in=usuarios_filtrados)

    # Inicializar contadores
    total_neumaticos = 0
    operativos_count = 0
    no_operativos_count = 0
    huella_0_3 = 0
    huella_3_6 = 0
    huella_6_mas = 0

    # Inicializar el contador de servicios
    servicios_por_vehiculo = {
        'alineacion': 0,
        'balanceo': 0,
        'rotacion': 0,
        'montura': 0,
        'calibracion': 0,
    }

    # Recorrer todos los neumáticos seleccionados
    for neumatico in neumaticos:
        total_neumaticos += 1

        # Verificar si tiene una avería de montura, lo que lo clasifica automáticamente como no operativo
        tiene_averia_montura = False
        for averia in neumatico.averias.all():
            if averia.servicio_requerido == 'montura':
                tiene_averia_montura = True
            # Sumar cada servicio requerido por la avería
            if averia.servicio_requerido in servicios_por_vehiculo:
                servicios_por_vehiculo[averia.servicio_requerido] += 1

        if not tiene_averia_montura and neumatico.huella > 0:
            # Es operativo
            operativos_count += 1

            # Clasificar la huella del neumático si es operativo
            if neumatico.huella <= 3:
                huella_0_3 += 1
            elif 3 < neumatico.huella <= 6:
                huella_3_6 += 1
            elif neumatico.huella >= 6:
                huella_6_mas += 1
        else:
            # Es no operativo si tiene avería de montura o huella = 0
            no_operativos_count += 1

    # Obtener todas las empresas para el autocompletado y la lista desplegable
    empresas = Usuario.objects.values_list('empresa', flat=True).distinct().exclude(is_superuser=True)
    empresas_json = json.dumps(list(empresas))  # Convertir a JSON para el autocompletar

    # Preparar el contexto para la vista
    context = {
        'total_neumaticos': total_neumaticos,
        'operativos': operativos_count,
        'no_operativos': no_operativos_count,
        'huella_0_3': huella_0_3,
        'huella_3_6': huella_3_6,
        'huella_6_mas': huella_6_mas,
        'servicios_por_vehiculo': servicios_por_vehiculo,
        'usuarios': usuarios_filtrados,
        'selected_user': selected_user,
        'empresas': empresas,
        'empresas_json': empresas_json,
        'selected_empresa': selected_empresa,
    }
    
    return render(request, 'index.html', context)


# Vista para usuarios normales (user_dashboard)
@login_required
@never_cache
def user_dashboard(request):
    return render(request, 'user_dashboard.html')

