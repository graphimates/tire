from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io
import json
from collections import Counter
import copy
from .models import Neumatico, MedidaNeumatico, HistorialInspeccion
from vehiculos.models import Vehiculo
from usuarios.models import Usuario
from averias.models import Averia
from .forms import NeumaticoForm, MedidaForm
from django.core.paginator import Paginator


# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser


# Vista para gestionar medidas
@login_required
@user_passes_test(is_admin)
def ver_medidas(request):
    medidas = MedidaNeumatico.objects.all()
    return render(request, 'medidas/ver_medidas.html', {'medidas': medidas})


# Vista para crear una nueva medida
@login_required
@user_passes_test(is_admin)
def crear_medida(request):
    if request.method == 'POST':
        form = MedidaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_medidas')
    else:
        form = MedidaForm()
    
    return render(request, 'medidas/crear_medida.html', {'form': form})


# Vista para editar una medida
@login_required
@user_passes_test(is_admin)
def editar_medida(request, medida_id):
    medida = get_object_or_404(MedidaNeumatico, id=medida_id)
    if request.method == 'POST':
        form = MedidaForm(request.POST, instance=medida)
        if form.is_valid():
            form.save()
            return redirect('ver_medidas')
    else:
        form = MedidaForm(instance=medida)
    
    return render(request, 'medidas/editar_medida.html', {'form': form, 'medida': medida})


# Vista para eliminar una medida
@login_required
@user_passes_test(is_admin)
def eliminar_medida(request, medida_id):
    medida = get_object_or_404(MedidaNeumatico, id=medida_id)

    # Verificar si la medida está asociada a algún neumático
    if Neumatico.objects.filter(medida=medida).exists():
        # Si existen neumáticos asociados, evitar la eliminación
        return render(request, 'medidas/eliminar_medida.html', {
            'error': 'No se puede eliminar esta medida porque está asociada a neumáticos.'
        })
    
    if request.method == 'POST':
        medida.delete()
        return redirect('ver_medidas')
    
    return render(request, 'medidas/eliminar_medida.html', {'medida': medida})


@login_required
@user_passes_test(is_admin)
def eliminar_neumatico_temporal(request, vehiculo_id, posicion):
    # Intentar obtener el neumático temporal y eliminarlo
    try:
        neumatico = Neumatico.objects.get(vehiculo_id=vehiculo_id, posicion=posicion, temp=True)
        neumatico.delete()
        print(f"Neumático temporal en posición {posicion} eliminado.")
    except Neumatico.DoesNotExist:
        print(f"No se encontró un neumático temporal en la posición {posicion}.")

    return HttpResponse(status=204)


# neumatico/views.py


@login_required
@user_passes_test(is_admin)
def editar_neumatico(request, vehiculo_id, posicion):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)

    # Intentamos obtener el neumático en la posición específica
    neumatico, created = Neumatico.objects.get_or_create(
        vehiculo=vehiculo,
        posicion=posicion,
        defaults={
            'modelo': '',
            'marca': '',
            'diseño': '',
            'dot': '',
            'presion': None,  # Permitir que el campo quede vacío
            'huella': 0.0,  # Asignar huella por defecto como 0.0
            'renovable': False
        }
    )

    if request.method == 'POST':
        form = NeumaticoForm(request.POST, instance=neumatico)

        if form.is_valid():
            try:
                # Si el neumático ya tenía fecha de inspección, crear un historial
                if neumatico.fecha_inspeccion:
                    HistorialInspeccion.objects.create(
                        vehiculo=vehiculo,
                        posicion=neumatico.posicion,
                        modelo=neumatico.modelo,
                        marca=neumatico.marca,
                        diseño=neumatico.diseño,  # Incluimos el campo diseño
                        presion=neumatico.presion,
                        huella=neumatico.huella,
                        dot=neumatico.dot,
                        fecha_inspeccion=neumatico.fecha_inspeccion,
                        medida=neumatico.medida.medida if neumatico.medida else 'Desconocida',
                        renovable=neumatico.renovable,
                        precio_estimado=neumatico.precio_estimado,
                        averia=neumatico.averias.first() if neumatico.averias.exists() else None,
                    )

                # Guardar los cambios en el neumático
                neumatico = form.save(commit=False)
                if not neumatico.fecha_inspeccion:
                    neumatico.fecha_inspeccion = timezone.now()
                neumatico.save()
                form.save_m2m()

                # Actualizar la última fecha de inspección del vehículo
                vehiculo.ultima_inspeccion = neumatico.fecha_inspeccion
                vehiculo.save()

                return redirect('reporte_vehiculos')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = NeumaticoForm(instance=neumatico)

    return render(request, 'neumaticos/editar_neumatico.html', {'form': form, 'neumatico': neumatico, 'vehiculo': vehiculo})

from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from .models import Neumatico, HistorialInspeccion
from .forms import NeumaticoForm
from django.utils import timezone
from django.core.exceptions import ValidationError
from vehiculos.models import Vehiculo
from django.http import JsonResponse, HttpResponseForbidden

@csrf_exempt
@login_required
@user_passes_test(is_admin)
def eliminar_neumatico_temporal(request, vehiculo_id, posicion):
    if request.method == 'POST':
        vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
        try:
            neumatico = Neumatico.objects.get(vehiculo=vehiculo, posicion=posicion, temp=True)
            neumatico.delete()
            return JsonResponse({'status': 'success'})
        except Neumatico.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Neumático temporal no encontrado.'}, status=404)
    else:
        return HttpResponseForbidden()
# Vista para ver neumáticos

@login_required
def ver_neumaticos(request):
    # Si el usuario es admin, puede ver todos los neumáticos
    if request.user.is_superuser:
        neumaticos = Neumatico.objects.select_related('vehiculo__usuario').all()
        empresas = Vehiculo.objects.values_list('usuario__empresa', flat=True).distinct()
    else:
        # Los usuarios normales solo pueden ver los neumáticos de sus propios vehículos
        neumaticos = Neumatico.objects.filter(vehiculo__usuario=request.user).select_related('vehiculo__usuario')
        empresas = []  # No mostrar empresas si no es superusuario

    # Filtros
    operatividad = request.GET.get('operatividad')
    huella = request.GET.get('huella')
    renovable = request.GET.get('renovable')
    search_empresa = request.GET.get('search_empresa', '').strip()
    selected_empresa = request.GET.get('selected_empresa', '')

    # Filtrar por empresa
    if selected_empresa and selected_empresa != 'todas':
        neumaticos = neumaticos.filter(vehiculo__usuario__empresa__iexact=selected_empresa)

    # Filtrar por búsqueda de empresa
    if search_empresa:
        neumaticos = neumaticos.filter(vehiculo__usuario__empresa__icontains=search_empresa)

    # Filtrar por operatividad
    if operatividad:
        if operatividad == 'operativo':
            neumaticos = neumaticos.exclude(averias__estado='no_operativo')
        elif operatividad == 'fuera_de_uso':
            neumaticos = neumaticos.filter(averias__estado='no_operativo')

    # Filtrar por huella
    if huella:
        if huella == '0_3':
            neumaticos = neumaticos.filter(huella__lte=3)
        elif huella == '3_6':
            neumaticos = neumaticos.filter(huella__gt=3, huella__lte=6)
        elif huella == '6_mas':
            neumaticos = neumaticos.filter(huella__gt=6)

    # Filtrar por renovabilidad
    if renovable:
        if renovable == 'si':
            neumaticos = neumaticos.filter(renovable=True)
        elif renovable == 'no':
            neumaticos = neumaticos.filter(renovable=False)

    # Paginación
    paginator = Paginator(neumaticos, 20)  # 20 neumáticos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calcular la última inspección
    if neumaticos.exists():
        # Obtener los vehículos únicos asociados a los neumáticos filtrados
        vehiculos = Vehiculo.objects.filter(neumaticos__in=neumaticos).distinct()
        # Obtener la última inspección entre estos vehículos
        ultima_inspeccion = vehiculos.order_by('-ultima_inspeccion').first()
    else:
        ultima_inspeccion = None

    return render(request, 'neumaticos/ver_neumaticos.html', {
        'neumaticos': page_obj,  # Pasar el objeto de paginación
        'empresas': empresas,
        'operatividad': operatividad,
        'huella': huella,
        'renovable': renovable,
        'search_empresa': search_empresa,
        'selected_empresa': selected_empresa,
        'page_obj': page_obj,  # Pasar el objeto de paginación al template
        'ultima_inspeccion': ultima_inspeccion,  # Agregar la última inspección al contexto
    })


# neumatico/views.py
from django.contrib.auth import get_user_model

Usuario = get_user_model()

from datetime import timedelta
from collections import Counter
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usuarios.models import Usuario

@login_required
def historico_datos(request, user_id=None):
    # Función auxiliar para obtener el índice del mes basado en la fecha de inspección
    def obtener_indice_mes(fecha):
        hoy = timezone.now().date()
        delta_meses = (hoy.year - fecha.year) * 12 + (hoy.month - fecha.month)
        return 5 - delta_meses if 0 <= delta_meses < 6 else None

    # Obtener el usuario seleccionado o el actual
    selected_user_id = request.GET.get('usuario_id', user_id)
    rango_fecha = request.GET.get('rango_fecha')  # Filtro de rango de fecha predefinido

    hoy = timezone.now().date()
    if rango_fecha == '1_semana':
        fecha_inicio = hoy - timedelta(weeks=1)
    elif rango_fecha == '1_mes':
        fecha_inicio = hoy - timedelta(days=30)
    elif rango_fecha == '3_meses':
        fecha_inicio = hoy - timedelta(days=90)
    elif rango_fecha == '6_meses':
        fecha_inicio = hoy - timedelta(days=180)
    else:
        fecha_inicio = None

    # Obtener el usuario seleccionado y filtrar los datos
    if request.user.is_superuser and selected_user_id and selected_user_id != "todas":
        selected_user = Usuario.objects.get(id=selected_user_id)
    elif selected_user_id == "todas":
        selected_user = None
    else:
        selected_user = request.user

    # Filtrar los neumáticos y el historial de inspecciones por usuario y fecha
    if selected_user:
        neumaticos_actuales = Neumatico.objects.filter(vehiculo__usuario=selected_user)
        historial_inspecciones = HistorialInspeccion.objects.filter(vehiculo__usuario=selected_user)
    else:
        neumaticos_actuales = Neumatico.objects.all()
        historial_inspecciones = HistorialInspeccion.objects.all()

    if fecha_inicio:
        neumaticos_actuales = neumaticos_actuales.filter(fecha_inspeccion__gte=fecha_inicio)
        historial_inspecciones = historial_inspecciones.filter(fecha_inspeccion__gte=fecha_inicio)

    # Inicializar los contadores para los neumáticos
    operativos_data = 0
    renovables_data = 0
    desperdicio_data = 0

    # Preparar datos para la gráfica (últimos 6 meses)
    meses_labels = [(hoy - timedelta(days=30 * i)).strftime('%B') for i in range(6)][::-1]  # Últimos 6 meses
    operativos_mes = [0] * 6
    renovables_mes = [0] * 6
    desperdicio_mes = [0] * 6
    perdida_mes = [0] * 6  # Lista para almacenar la pérdida mensual

    # Valores de Y según el tipo de neumático
    y_values = {
        'direccional': 15,
        'tracción': 22,
        'traccion': 22,  # Por si acaso
        'all position': 18,
    }

    # Procesar neumáticos actuales
    for neumatico in neumaticos_actuales:
        fecha_inspeccion = neumatico.fecha_inspeccion.date() if neumatico.fecha_inspeccion else None
        indice_mes = obtener_indice_mes(fecha_inspeccion)
        if indice_mes is not None:
            # Contar operativos, renovables y desperdicio
            if neumatico.averias.filter(estado='no_operativo').exists():
                desperdicio_data += 1
                desperdicio_mes[indice_mes] += 1

                # Cálculo de Pérdida
                tipo_neumatico = neumatico.modelo.lower() if neumatico.modelo else ''
                Y = y_values.get(tipo_neumatico)
                if Y and neumatico.huella and neumatico.precio_estimado:
                    perdida = (neumatico.huella * float(neumatico.precio_estimado)) / Y
                    perdida_mes[indice_mes] += perdida
            else:
                operativos_data += 1
                operativos_mes[indice_mes] += 1
                if neumatico.renovable:
                    renovables_data += 1
                    renovables_mes[indice_mes] += 1

    # Procesar historial de inspecciones
    for inspeccion in historial_inspecciones:
        fecha_inspeccion = inspeccion.fecha_inspeccion.date() if inspeccion.fecha_inspeccion else None
        indice_mes = obtener_indice_mes(fecha_inspeccion)
        if indice_mes is not None:
            if inspeccion.averia and inspeccion.averia.estado == 'no_operativo':
                desperdicio_data += 1
                desperdicio_mes[indice_mes] += 1

                # Cálculo de Pérdida
                tipo_neumatico = inspeccion.modelo.lower() if inspeccion.modelo else ''
                Y = y_values.get(tipo_neumatico)
                if Y and inspeccion.huella and inspeccion.precio_estimado:
                    perdida = (inspeccion.huella * float(inspeccion.precio_estimado)) / Y
                    perdida_mes[indice_mes] += perdida
            else:
                operativos_data += 1
                operativos_mes[indice_mes] += 1
                if inspeccion.renovable:
                    renovables_data += 1
                    renovables_mes[indice_mes] += 1

    # Preparar los datos de averías para la gráfica de averías
    averias_counter = Counter()
    for neumatico in neumaticos_actuales:
        for averia in neumatico.averias.all():
            averias_counter[averia.nombre] += 1
    for inspeccion in historial_inspecciones:
        if inspeccion.averia:
            averias_counter[inspeccion.averia.nombre] += 1

    averias_ordenadas = sorted(averias_counter.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0] for item in averias_ordenadas]
    data_barras = [item[1] for item in averias_ordenadas]
    total_averias = sum(data_barras)
    data_barras_porcentaje = [(cantidad / total_averias) * 100 for cantidad in data_barras] if total_averias > 0 else []

    # Porcentaje acumulado de averías
    porcentaje_acumulado = []
    suma_acumulada = 0
    for cantidad in data_barras:
        suma_acumulada += cantidad
        porcentaje_acumulado.append(round((suma_acumulada / total_averias) * 100, 2)) if total_averias > 0 else []

    # Obtener la última inspección
    if historial_inspecciones.exists():
        ultima_inspeccion = historial_inspecciones.order_by('-fecha_inspeccion').first()
    else:
        ultima_inspeccion = None

    context = {
        'labels': labels,
        'data_barras': data_barras_porcentaje,
        'porcentaje_acumulado': porcentaje_acumulado,
        'usuarios': Usuario.objects.exclude(is_superuser=True),
        'selected_user': selected_user,
        'averias_counter': dict(averias_counter),
        'operativos_data': operativos_data,
        'renovables_data': renovables_data,
        'desperdicio_data': desperdicio_data,
        'cauchos_labels': ['Operativos', 'Renovables', 'Desperdicio'],
        'datos_grafica': [operativos_data, renovables_data, desperdicio_data],
        'meses_labels': meses_labels,
        'operativos_mes': operativos_mes,
        'renovables_mes': renovables_mes,
        'desperdicio_mes': desperdicio_mes,
        'perdida_mes': perdida_mes,  # Pérdida por mes
        'ultima_inspeccion': ultima_inspeccion,  # Última inspección
    }

    return render(request, 'neumaticos/historico_datos.html', context)



# neumatico/views.py
@login_required
@user_passes_test(is_admin)
def cargar_inspecciones(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        # Verificar que el archivo es un CSV
        if not csv_file.name.endswith('.csv'):
            context = {'errores': ['Por favor, suba un archivo CSV válido.']}
            return render(request, 'neumaticos/cargar_inspecciones.html', context)

        try:
            decoded_file = csv_file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded_file), delimiter=';')
        except Exception as e:
            context = {'errores': [f'Error al procesar el archivo CSV: {str(e)}']}
            return render(request, 'neumaticos/cargar_inspecciones.html', context)

        errores = []
        inspecciones_pendientes = []
        inspecciones_agrupadas = {}

        for row in reader:
            # Inicializamos las variables
            cliente_email = row.get('cliente', '').strip()
            placa = row.get('placa', '').strip()
            posicion_str = row.get('posicion', '').strip()
            medida_str = row.get('medida', '').strip()
            dot = row.get('dot', '').strip()
            presion_str = row.get('presion', '').strip()
            huella_str = row.get('huella', '').strip()
            modelo = row.get('modelo', '').strip().lower()
            averias_str = row.get('averia', '').strip()
            renovable = row.get('renovable', '').strip().lower() == 'true'

            hay_error_en_inspeccion = False

            # Validación de cliente
            if not cliente_email:
                errores.append('El campo "cliente" es obligatorio.')
                hay_error_en_inspeccion = True
            else:
                try:
                    cliente = Usuario.objects.get(email=cliente_email)
                except Usuario.DoesNotExist:
                    errores.append(f"El cliente con el correo {cliente_email} no existe.")
                    hay_error_en_inspeccion = True

            # Validación de vehículo
            if not placa:
                errores.append('El campo "placa" es obligatorio.')
                hay_error_en_inspeccion = True
            else:
                try:
                    vehiculo = Vehiculo.objects.get(placa=placa, usuario=cliente)
                except Vehiculo.DoesNotExist:
                    errores.append(f"El vehículo con la placa {placa} no existe para el cliente {cliente_email}.")
                    hay_error_en_inspeccion = True

            if hay_error_en_inspeccion:
                continue  # Saltar el procesamiento de esta fila

            # Validación de posición
            cantidad_neumaticos = vehiculo.cantidad_neumaticos
            if not posicion_str:
                errores.append(f"Falta la posición para un neumático del vehículo con placa {placa}.")
                hay_error_en_inspeccion = True
            else:
                try:
                    posicion = int(posicion_str)
                    if posicion < 1 or posicion > cantidad_neumaticos:
                        errores.append(f"La posición {posicion} no es válida para un vehículo con {cantidad_neumaticos} neumáticos.")
                        hay_error_en_inspeccion = True
                except ValueError:
                    errores.append(f"La posición {posicion_str} no es un número válido.")
                    hay_error_en_inspeccion = True

            if hay_error_en_inspeccion:
                continue  # Saltar el procesamiento de esta fila

            # Validar la medida
            if not medida_str:
                errores.append(f"Falta la medida para un neumático en la posición {posicion} del vehículo con placa {placa}.")
                continue

            try:
                medida = MedidaNeumatico.objects.get(medida=medida_str)
            except MedidaNeumatico.DoesNotExist:
                errores.append(f"La medida {medida_str} no está registrada.")
                continue

            # Validar presión y huella
            try:
                presion = float(presion_str)
            except ValueError:
                errores.append(f"La presión en la posición {posicion} del vehículo con placa {placa} no es un número válido.")
                continue

            try:
                huella = float(huella_str)
                if huella < 0:
                    errores.append(f"La huella no puede ser menor a 0 en la posición {posicion} del vehículo con placa {placa}.")
                    continue
            except ValueError:
                errores.append(f"La huella en la posición {posicion} del vehículo con placa {placa} no es un número válido.")
                continue

            # Validar y procesar las averías
            averias = []
            if averias_str:
                averia_codigos = [codigo.strip() for codigo in averias_str.split(',')]
                for codigo in averia_codigos:
                    try:
                        averia = Averia.objects.get(codigo=codigo)
                        averias.append(averia)
                    except Averia.DoesNotExist:
                        errores.append(f"La avería con código {codigo} no está registrada.")

            # Validar 'renovable' según las averías
            if averias:
                if any(averia.estado == 'no_operativo' for averia in averias) and renovable:
                    errores.append(f"El neumático en posición {posicion} del vehículo con placa {placa} no puede ser renovable si tiene una avería 'No operativo'.")
                    renovable = False

            # Recolectar los datos para inspecciones pendientes
            inspeccion = {
                'cliente': cliente_email,
                'placa': placa,
                'posicion': posicion,
                'medida': medida_str,
                'marca': row.get('marca', '').strip(),
                'diseño': row.get('diseño', '').strip(),
                'dot': dot,
                'presion': presion,
                'huella': huella,
                'averias': [averia.codigo for averia in averias],
                'renovable': renovable,
                'modelo': modelo,
                'fecha_inspeccion': row.get('fecha', '').strip() or timezone.now().strftime('%d/%m/%Y'),
            }
            inspecciones_pendientes.append(inspeccion)

            # Agrupar para previsualización
            key = (cliente_email, placa)
            if key not in inspecciones_agrupadas:
                inspecciones_agrupadas[key] = []
            inspecciones_agrupadas[key].append(inspeccion)

        if errores:
            context = {'errores': errores}
            return render(request, 'neumaticos/cargar_inspecciones.html', context)
        else:
            request.session['inspecciones_pendientes'] = inspecciones_pendientes
            context = {'inspecciones_agrupadas': inspecciones_agrupadas}
            return render(request, 'neumaticos/cargar_inspecciones.html', context)

    return render(request, 'neumaticos/cargar_inspecciones.html')


# neumatico/views.py

@login_required
@user_passes_test(is_admin)
def confirmar_inspecciones(request):
    if request.method == 'POST':
        inspecciones_pendientes = request.session.get('inspecciones_pendientes', [])
        errores = []

        for inspeccion in inspecciones_pendientes:
            cliente_email = inspeccion['cliente']
            placa = inspeccion['placa']
            posicion = inspeccion['posicion']

            try:
                cliente = Usuario.objects.get(email=cliente_email)
                vehiculo = Vehiculo.objects.get(placa=placa, usuario=cliente)
            except (Usuario.DoesNotExist, Vehiculo.DoesNotExist):
                errores.append(f"Cliente o vehículo no encontrado: Cliente {cliente_email}, Placa {placa}.")
                continue  # Saltar esta inspección

            try:
                medida = MedidaNeumatico.objects.get(medida=inspeccion['medida'])
            except MedidaNeumatico.DoesNotExist:
                errores.append(f"La medida {inspeccion['medida']} no está registrada.")
                continue  # Saltar esta inspección

            # Procesar averías
            averias_codigos = inspeccion.get('averias', [])
            averias = []
            if averias_codigos:
                for codigo in averias_codigos:
                    try:
                        averia = Averia.objects.get(codigo=codigo)
                        averias.append(averia)
                    except Averia.DoesNotExist:
                        errores.append(f"La avería con código {codigo} no está registrada para el neumático en posición {inspeccion['posicion']} del vehículo con placa {inspeccion['placa']}.")
                # Continuar con las averías válidas

            renovable = inspeccion['renovable']

            # Validar 'renovable' según las averías válidas
            if averias:
                if any(averia.estado == 'no_operativo' for averia in averias) and renovable:
                    errores.append(f"El neumático en posición {posicion} del vehículo con placa {placa} no puede ser renovable si tiene una avería 'No operativo'.")
                    renovable = False

            # Convertir la fecha al formato correcto
            fecha_inspeccion_str = inspeccion['fecha_inspeccion']
            try:
                fecha_inspeccion = datetime.strptime(fecha_inspeccion_str, '%d/%m/%Y').date()
            except ValueError:
                errores.append(f"La fecha '{fecha_inspeccion_str}' no tiene un formato válido (se espera DD/MM/YYYY).")
                continue  # Saltar esta inspección si la fecha no es válida

            # Obtener o crear el neumático
            neumatico, created = Neumatico.objects.get_or_create(
                vehiculo=vehiculo,
                posicion=posicion,
                defaults={
                    'modelo': inspeccion['modelo'],
                    'marca': inspeccion['marca'],
                    'diseño': inspeccion['diseño'],  # Incluimos el diseño en los defaults
                    'dot': inspeccion['dot'],
                    'presion': inspeccion['presion'],
                    'huella': inspeccion['huella'],
                    'medida': medida,
                    'renovable': renovable,
                    'fecha_inspeccion': fecha_inspeccion,
                }
            )

            if not created:
                # Guardar en el historial si ha sido inspeccionado antes
                if neumatico.fecha_inspeccion:
                    HistorialInspeccion.objects.create(
                        vehiculo=vehiculo,
                        posicion=neumatico.posicion,
                        modelo=neumatico.modelo,
                        marca=neumatico.marca,
                        diseño=neumatico.diseño,  # Incluimos el campo diseño
                        presion=neumatico.presion,
                        huella=neumatico.huella,
                        dot=neumatico.dot,
                        fecha_inspeccion=neumatico.fecha_inspeccion,
                        medida=neumatico.medida.medida if neumatico.medida else 'Desconocida',
                        renovable=neumatico.renovable,
                        precio_estimado=neumatico.precio_estimado,
                        averia=neumatico.averias.first() if neumatico.averias.exists() else None,
                    )
                # Actualizar el neumático existente
                neumatico.modelo = inspeccion['modelo']
                neumatico.marca = inspeccion['marca']
                neumatico.diseño = inspeccion['diseño']
                neumatico.dot = inspeccion['dot']
                neumatico.presion = inspeccion['presion']
                neumatico.huella = inspeccion['huella']
                neumatico.medida = medida
                neumatico.renovable = renovable
                neumatico.fecha_inspeccion = fecha_inspeccion
                neumatico.save()

            # Establecer las averías (asegurándonos de que el neumático está guardado)
            neumatico.averias.set(averias)
            neumatico.save()

            # Actualizar la última inspección del vehículo
            vehiculo.ultima_inspeccion = fecha_inspeccion
            vehiculo.save()

        if errores:
            context = {'errores': errores}
            return render(request, 'neumaticos/cargar_inspecciones.html', context)

        # Limpiar los datos de la sesión
        request.session.pop('inspecciones_pendientes', None)
        return redirect('reporte_vehiculos')

    return redirect('cargar_inspecciones')





# neumatico/views.py (modificada)
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

    return render(request, 'vehiculos/editar_fecha.html', {'vehiculo': vehiculo})
