from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime
import csv
import io
import json  # Asegúrate de importar json
from collections import Counter
import copy
from .models import Neumatico, MedidaNeumatico, HistorialInspeccion
from vehiculos.models import Vehiculo
from usuarios.models import Usuario
from averias.models import Averia
from .forms import NeumaticoForm, MedidaForm


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


# neumatico/views.py (modificada)

@login_required
@user_passes_test(is_admin)
def editar_neumatico(request, vehiculo_id, posicion):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    neumatico = get_object_or_404(Neumatico, vehiculo=vehiculo, posicion=posicion)

    if request.method == 'POST':
        # Hacer una copia del estado actual del neumático antes de procesar el formulario
        old_neumatico = copy.copy(neumatico)

        form = NeumaticoForm(request.POST, instance=neumatico)
        if form.is_valid():
            try:
                # Guardar el historial solo si el neumático ya tiene una fecha de inspección anterior
                if old_neumatico.fecha_inspeccion:
                    HistorialInspeccion.objects.create(
                        vehiculo=vehiculo,
                        posicion=old_neumatico.posicion,
                        modelo=old_neumatico.modelo,
                        marca=old_neumatico.marca,
                        presion=old_neumatico.presion,
                        huella=old_neumatico.huella,
                        dot=old_neumatico.dot,
                        fecha_inspeccion=old_neumatico.fecha_inspeccion,
                        medida=old_neumatico.medida.medida if old_neumatico.medida else 'Desconocida',
                        renovable=old_neumatico.renovable,
                        precio_estimado=old_neumatico.precio_estimado,
                        averia=old_neumatico.averias.first() if old_neumatico.averias.exists() else None,
                    )

                # Ahora guardamos los cambios del formulario
                neumatico = form.save(commit=False)
                
                # Si no se seleccionó fecha, asignar la fecha actual
                if not neumatico.fecha_inspeccion:
                    neumatico.fecha_inspeccion = timezone.now()

                neumatico.save()
                form.save_m2m()  # Guardar las relaciones ManyToMany

                # Actualizar la fecha de última inspección del vehículo
                vehiculo.ultima_inspeccion = neumatico.fecha_inspeccion
                vehiculo.save()

                return redirect('reporte_vehiculos')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = NeumaticoForm(instance=neumatico)

    return render(request, 'neumaticos/editar_neumatico.html', {'form': form, 'neumatico': neumatico})


# Vista para ver neumáticos
@login_required
def ver_neumaticos(request):
    # Si el usuario es admin, puede ver todos los neumáticos
    if request.user.is_superuser:
        neumaticos = Neumatico.objects.select_related('vehiculo').all()
    else:
        # Los usuarios normales solo pueden ver los neumáticos de sus propios vehículos
        neumaticos = Neumatico.objects.filter(vehiculo__usuario=request.user)

    # Filtros de búsqueda y operatividad
    operatividad = request.GET.get('operatividad')
    huella = request.GET.get('huella')
    renovable = request.GET.get('renovable')
    ordenar = request.GET.get('ordenar', 'reciente')

    # Filtrar por operatividad
    if operatividad:
        if operatividad == 'operativo':
            # Filtramos por neumáticos que no tienen averías "no operativo"
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

    # Ordenar por la fecha de inspección
    if ordenar == 'reciente':
        neumaticos = neumaticos.order_by('-vehiculo__ultima_inspeccion')
    elif ordenar == 'antigua':
        neumaticos = neumaticos.order_by('vehiculo__ultima_inspeccion')

    return render(request, 'neumaticos/ver_neumaticos.html', {
        'neumaticos': neumaticos,
        'operatividad': operatividad,
        'huella': huella,
        'renovable': renovable,
        'ordenar': ordenar
    })


from django.db.models import Count
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
@login_required
def historico_datos(request, user_id=None):
    from datetime import timedelta

    # Función auxiliar corregida
    def obtener_indice_mes(fecha):
        """Función para obtener el índice del mes basado en la fecha de inspección.
        Considera los últimos 6 meses desde la fecha actual."""
        if fecha:
            hoy = timezone.now().date()
            delta_meses = (hoy.year - fecha.year) * 12 + (hoy.month - fecha.month)
            # Aceptar solo los últimos 6 meses
            if 0 <= delta_meses < 6:
                return 5 - delta_meses
        return None

    # Obtener el usuario seleccionado o el actual
    selected_user_id = request.GET.get('usuario_id', user_id)
    if request.user.is_superuser:
        selected_user = Usuario.objects.get(id=selected_user_id)
    else:
        selected_user = request.user

    # Obtener los neumáticos actuales y el historial de inspecciones del usuario seleccionado
    neumaticos_actuales = Neumatico.objects.filter(vehiculo__usuario=selected_user)
    historial_inspecciones = HistorialInspeccion.objects.filter(vehiculo__usuario=selected_user)

    # Inicializar los contadores para los neumáticos
    operativos_data = 0
    renovables_data = 0
    desperdicio_data = 0

    # Preparar datos para la nueva gráfica (últimos 6 meses)
    hoy = timezone.now().date()
    meses_labels = [(hoy - timedelta(days=30*i)).strftime('%B') for i in range(6)][::-1]  # Últimos 6 meses
    operativos_mes = [0] * 6
    renovables_mes = [0] * 6
    desperdicio_mes = [0] * 6

    # Contar los neumáticos actuales por su estado y mes de inspección
    for neumatico in neumaticos_actuales:
        indice_mes = obtener_indice_mes(neumatico.fecha_inspeccion)
        if indice_mes is not None:
            if neumatico.renovable:
                renovables_data += 1
                renovables_mes[indice_mes] += 1
            elif neumatico.averias.filter(estado='no_operativo').exists():
                desperdicio_data += 1
                desperdicio_mes[indice_mes] += 1
            else:
                operativos_data += 1
                operativos_mes[indice_mes] += 1

    # Contar los neumáticos en el historial por su estado y mes
    for inspeccion in historial_inspecciones:
        indice_mes = obtener_indice_mes(inspeccion.fecha_inspeccion)
        if indice_mes is not None:
            if inspeccion.renovable:
                renovables_data += 1
                renovables_mes[indice_mes] += 1
            elif inspeccion.averia and inspeccion.averia.estado == 'no_operativo':
                desperdicio_data += 1
                desperdicio_mes[indice_mes] += 1
            else:
                operativos_data += 1
                operativos_mes[indice_mes] += 1

    # Etiquetas para la gráfica
    cauchos_labels = ['Operativos', 'Renovables', 'Desperdicio']

    # Datos de la gráfica
    datos_grafica = [operativos_data, renovables_data, desperdicio_data]

    # Preparar los datos de averías para la otra gráfica
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
    data_barras_porcentaje = [(cantidad / total_averias) * 100 for cantidad in data_barras]

    # Porcentaje acumulado de averías
    porcentaje_acumulado = []
    suma_acumulada = 0
    for cantidad in data_barras:
        suma_acumulada += cantidad
        porcentaje_acumulado.append(round((suma_acumulada / total_averias) * 100, 2))

    context = {
        'labels': labels,
        'data_barras': data_barras_porcentaje,
        'porcentaje_acumulado': porcentaje_acumulado,
        'usuarios': Usuario.objects.all(),
        'selected_user': selected_user,
        'averias_counter': dict(averias_counter),
        'operativos_data': operativos_data,
        'renovables_data': renovables_data,
        'desperdicio_data': desperdicio_data,
        'cauchos_labels': cauchos_labels,
        'datos_grafica': datos_grafica,
        'meses_labels': meses_labels,
        'operativos_mes': operativos_mes,
        'renovables_mes': renovables_mes,
        'desperdicio_mes': desperdicio_mes,
    }

    return render(request, 'neumaticos/historico_datos.html', context)



# neumatico/views.py


def is_admin(user):
    return user.is_superuser

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

            # Flag para identificar errores en la inspección
            hay_error_en_inspeccion = False

            # Validación y recolección de datos
            if not cliente_email:
                errores.append('El campo "cliente" es obligatorio.')
                hay_error_en_inspeccion = True
            else:
                try:
                    cliente = Usuario.objects.get(email=cliente_email)
                except Usuario.DoesNotExist:
                    errores.append(f"El cliente con el correo {cliente_email} no existe.")
                    hay_error_en_inspeccion = True

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

            # Validar presión
            try:
                presion = float(presion_str)
            except ValueError:
                errores.append(f"La presión en la posición {posicion} del vehículo con placa {placa} no es un número válido.")
                continue

            # Validar huella
            try:
                huella = float(huella_str)
                if huella < 0:
                    errores.append(f"La huella no puede ser menor a 0 en la posición {posicion} del vehículo con placa {placa}.")
                    continue
            except ValueError:
                errores.append(f"La huella en la posición {posicion} del vehículo con placa {placa} no es un número válido.")
                continue

            # Validar campo 'dot' (no puede estar vacío)
            if not dot:
                errores.append(f"El campo 'dot' es obligatorio para el neumático en posición {posicion} del vehículo con placa {placa}.")
                continue

            # Validar campo 'modelo'
            modelos_validos = ['direccional', 'traccion', 'all position']
            if modelo not in modelos_validos:
                errores.append(f"El modelo '{modelo}' no es válido para el neumático en posición {posicion} del vehículo con placa {placa}. Opciones válidas: Direccional, Tracción, All Position.")
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
                # Continuamos con las averías válidas

            # Validar 'renovable' según las averías válidas
            if averias:
                if any(averia.estado == 'no_operativo' for averia in averias) and renovable:
                    errores.append(f"El neumático en posición {posicion} del vehículo con placa {placa} no puede ser renovable si tiene una avería 'No operativo'.")
                    renovable = False

            # Fecha de inspección
            fecha_inspeccion_str = row.get('fecha', '').strip()
            if fecha_inspeccion_str:
                try:
                    fecha_inspeccion = datetime.strptime(fecha_inspeccion_str, '%d/%m/%Y')
                except ValueError:
                    errores.append(f"La fecha '{fecha_inspeccion_str}' no tiene un formato válido (se espera dd/mm/yyyy).")
                    continue
            else:
                fecha_inspeccion = timezone.now()

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
                'averias': [averia.codigo for averia in averias],  # Averías válidas
                'renovable': renovable,
                'modelo': modelo,
                'fecha_inspeccion': fecha_inspeccion.strftime('%d/%m/%Y'),
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
                # Convertir la fecha de DD/MM/YYYY a YYYY-MM-DD
                fecha_inspeccion = datetime.strptime(fecha_inspeccion_str, '%d/%m/%Y').date()
            except ValueError:
                errores.append(f"La fecha '{fecha_inspeccion_str}' no tiene un formato válido (se espera DD/MM/YYYY).")
                continue  # Saltar esta inspección si la fecha no es válida

            # Procesar el neumático
            try:
                neumatico = Neumatico.objects.get(vehiculo=vehiculo, posicion=posicion)
                # Guardar en el historial si ha sido inspeccionado antes
                if neumatico.fecha_inspeccion:
                    HistorialInspeccion.objects.create(
                        vehiculo=vehiculo,
                        posicion=neumatico.posicion,
                        modelo=neumatico.modelo,
                        marca=neumatico.marca,
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
                neumatico.fecha_inspeccion = fecha_inspeccion  # Asignar la fecha correctamente formateada
                neumatico.save()
                # Actualizar averías
                neumatico.averias.set(averias)

            except Neumatico.DoesNotExist:
                # Crear un nuevo neumático
                neumatico = Neumatico.objects.create(
                    vehiculo=vehiculo,
                    posicion=posicion,
                    modelo=inspeccion['modelo'],
                    marca=inspeccion['marca'],
                    diseño=inspeccion['diseño'],
                    dot=inspeccion['dot'],
                    presion=inspeccion['presion'],
                    huella=inspeccion['huella'],
                    medida=medida,
                    renovable=renovable,
                    fecha_inspeccion=fecha_inspeccion,  # Asignar la fecha correctamente formateada
                )
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
