from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from neumatico.models import Neumatico
from usuarios.models import Usuario  # Asegúrate de que estás usando el modelo correcto

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from averias.models import Averia

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
    # Si el usuario es admin puede seleccionar otros usuarios
    selected_user_id = request.GET.get('usuario_id')
    if request.user.is_superuser:
        if selected_user_id:
            selected_user = Usuario.objects.get(id=selected_user_id)
        else:
            selected_user = request.user  # El admin puede ver sus propios datos como predeterminado
    else:
        selected_user = request.user

    # Obtener todos los neumáticos del usuario seleccionado
    neumaticos = Neumatico.objects.filter(vehiculo__usuario=selected_user)

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

    # Recorrer todos los neumáticos del usuario seleccionado
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

    # Obtener todos los usuarios (solo visible para el admin)
    usuarios = Usuario.objects.all() if request.user.is_superuser else None

    # Preparar el contexto para la vista
    context = {
        'total_neumaticos': total_neumaticos,
        'operativos': operativos_count,
        'no_operativos': no_operativos_count,
        'huella_0_3': huella_0_3,
        'huella_3_6': huella_3_6,
        'huella_6_mas': huella_6_mas,
        'servicios_por_vehiculo': servicios_por_vehiculo,
        'usuarios': usuarios,
        'selected_user': selected_user,
    }
    
    return render(request, 'index.html', context)


# Vista para usuarios normales (user_dashboard)
@login_required
@never_cache
def user_dashboard(request):
    return render(request, 'user_dashboard.html')
