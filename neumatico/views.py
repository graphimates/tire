from django.shortcuts import render, get_object_or_404, redirect
from .models import Neumatico, HistorialInspeccion, MedidaNeumatico
from vehiculos.models import Vehiculo
from usuarios.models import Usuario
from averias.models import Averia
from .forms import NeumaticoForm, MedidaForm
from django.utils import timezone
from collections import Counter
from django.contrib.auth.decorators import login_required, user_passes_test
import csv
import io
from django.http import HttpResponse
from django.core.exceptions import ValidationError

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
@user_passes_test(lambda u: u.is_superuser)
def crear_neumatico(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)

    if request.method == 'POST':
        valid_forms = True

        # Capturar la fecha anterior de inspección ANTES de actualizar los neumáticos
        fecha_anterior_inspeccion = vehiculo.ultima_inspeccion

        # Guardar los neumáticos actuales en el historial antes de eliminarlos
        for neumatico in vehiculo.neumaticos.all():
            HistorialInspeccion.objects.create(
                vehiculo=vehiculo,
                posicion=neumatico.posicion,
                modelo=neumatico.modelo,
                marca=neumatico.marca,
                presion=neumatico.presion,
                huella=neumatico.huella,
                dot=neumatico.dot,
                fecha_inspeccion=fecha_anterior_inspeccion,  # Usar la fecha ANTERIOR de inspección
                medida=neumatico.medida.medida if neumatico.medida else 'Desconocida',
                renovable=neumatico.renovable,
                precio_estimado=neumatico.precio_estimado,
                averia=neumatico.averias.first() if neumatico.averias.exists() else None,  # Añadir la avería
            )

        # Eliminar los neumáticos actuales para reemplazarlos con los nuevos datos
        vehiculo.neumaticos.all().delete()

        # Procesar los formularios de nuevos neumáticos
        for posicion in range(1, vehiculo.cantidad_neumaticos + 1):
            form = NeumaticoForm(request.POST, prefix=f'neumatico_{posicion}')

            if form.is_valid():
                neumatico = form.save(commit=False)
                neumatico.vehiculo = vehiculo
                neumatico.posicion = posicion

                if not neumatico.medida:
                    form.add_error('medida', 'La medida seleccionada no es válida.')
                    valid_forms = False
                else:
                    neumatico.actualizar_precio()
                    neumatico.save()

                    if 'montura' in [averia.servicio_requerido for averia in form.cleaned_data['averias']]:
                        neumatico.renovable = False

                    form.save_m2m()
            else:
                valid_forms = False
                print(f"Formulario de posición {posicion} no es válido: {form.errors}")

        # Si todos los formularios son válidos, actualizar la fecha de inspección del vehículo
        if valid_forms:
            vehiculo.ultima_inspeccion = timezone.now()  # Actualizar la fecha de la última inspección
            vehiculo.save()
            return redirect('reporte_vehiculos')

    forms = [NeumaticoForm(prefix=f'neumatico_{posicion}') for posicion in range(1, vehiculo.cantidad_neumaticos + 1)]
    return render(request, 'neumaticos/crear_neumatico.html', {'forms': forms, 'vehiculo': vehiculo})




# Vista para ver neumáticos
@login_required
def ver_neumaticos(request):
    neumaticos = Neumatico.objects.select_related('vehiculo').all()
    return render(request, 'neumaticos/ver_neumaticos.html', {'neumaticos': neumaticos})



@login_required
def historico_datos(request, user_id=None):
    # Obtener el usuario seleccionado o el actual
    selected_user_id = request.GET.get('usuario_id', user_id)
    if request.user.is_superuser:
        selected_user = Usuario.objects.get(id=selected_user_id)
    else:
        selected_user = request.user

    # Obtener todos los neumáticos del usuario seleccionado (incluyendo los de la última inspección)
    neumaticos = Neumatico.objects.filter(vehiculo__usuario=selected_user)
    
    # Inicializar un contador de averías
    averias_counter = Counter()

    # Recorrer los neumáticos y contar las averías de la última inspección
    for neumatico in neumaticos:
        for averia in neumatico.averias.all():
            averias_counter[averia.nombre] += 1
    
    # Recorrer el historial de inspecciones y contar las averías
    historial_inspecciones = HistorialInspeccion.objects.filter(vehiculo__usuario=selected_user)
    for inspeccion in historial_inspecciones:
        if inspeccion.averia:
            averias_counter[inspeccion.averia.nombre] += 1
    
    # Obtener las averías más frecuentes y ordenarlas de mayor a menor
    averias_ordenadas = sorted(averias_counter.items(), key=lambda x: x[1], reverse=True)

    # Preparar los datos para la gráfica
    labels = [item[0] for item in averias_ordenadas]  # Nombres de las averías
    data_barras = [item[1] for item in averias_ordenadas]  # Frecuencias de las averías

    # Calcular el total de averías
    total_averias = sum(data_barras)

    # Convertir a porcentaje
    data_barras_porcentaje = [(cantidad / total_averias) * 100 for cantidad in data_barras]

    # Calcular el porcentaje acumulativo para la línea
    porcentaje_acumulado = []
    suma_acumulada = 0
    for cantidad in data_barras:
        suma_acumulada += cantidad
        porcentaje_acumulado.append(round((suma_acumulada / total_averias) * 100, 2))

    context = {
        'labels': labels,
        'data_barras': data_barras_porcentaje,  # Enviar los porcentajes en lugar de los valores absolutos
        'porcentaje_acumulado': porcentaje_acumulado,
        'usuarios': Usuario.objects.all(),
        'selected_user': selected_user,
        'averias_counter': dict(averias_counter)  # Convertir el Counter a un diccionario para pasarlo al template
    }
    
    return render(request, 'neumaticos/historico_datos.html', context)


@login_required
@user_passes_test(is_admin)
def cargar_inspecciones(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded_file), delimiter=';')

        errores = []
        filas_previsualizacion = []
        inspecciones_pendientes = []
        inspecciones_agrupadas = {}

        for row in reader:
            cliente_email = row['cliente'].strip()
            try:
                cliente = Usuario.objects.get(email=cliente_email)
            except Usuario.DoesNotExist:
                errores.append(f"El cliente con el correo {cliente_email} no existe.")
                continue

            placa = row['placa'].strip()
            try:
                vehiculo = Vehiculo.objects.get(placa=placa, usuario=cliente)
            except Vehiculo.DoesNotExist:
                errores.append(f"El vehículo con la placa {placa} no existe para el cliente {cliente_email}.")
                continue

            cantidad_neumaticos = vehiculo.cantidad_neumaticos

            if not row['posicion']:
                errores.append(f"Falta la posición para un neumático del vehículo con placa {placa}.")
                continue

            try:
                posicion = int(row['posicion'])
                if posicion < 1 or posicion > cantidad_neumaticos:
                    errores.append(f"La posición {posicion} no es válida para un vehículo con {cantidad_neumaticos} neumáticos.")
                    continue
            except ValueError:
                errores.append(f"La posición {row['posicion']} no es un número válido.")
                continue

            if posicion in [inspeccion['posicion'] for inspeccion in inspecciones_pendientes if inspeccion['placa'] == placa]:
                errores.append(f"La posición {posicion} está duplicada para el vehículo con placa {placa}.")
                continue

            if not row['medida']:
                errores.append(f"Falta la medida para un neumático en la posición {posicion} del vehículo con placa {placa}.")
                continue

            try:
                medida = MedidaNeumatico.objects.get(medida=row['medida'])
            except MedidaNeumatico.DoesNotExist:
                errores.append(f"La medida {row['medida']} no está registrada.")
                continue

            # Note: We will handle empty 'averia' fields later.

            # Agregando 'modelo' y 'diseño' a la inspección
            inspeccion = {
                'cliente': cliente_email,
                'placa': placa,
                'posicion': posicion,
                'medida': row['medida'],
                'marca': row['marca'],
                'dot': row['dot'],
                'presion': row['presion'],
                'huella': row['huella'],
                'averia': row.get('averia', '').strip(),  # Get 'averia' or empty string
                'renovable': row['renovable'],
                'modelo': row.get('modelo', 'No especificado'),
                'diseño': row.get('diseño', 'No especificado')
            }
            inspecciones_pendientes.append(inspeccion)

            key = (cliente_email, placa)
            if key not in inspecciones_agrupadas:
                inspecciones_agrupadas[key] = []
            inspecciones_agrupadas[key].append(inspeccion)

        if not errores:
            request.session['inspecciones_pendientes'] = inspecciones_pendientes
            context = {
                'inspecciones_agrupadas': inspecciones_agrupadas,
                'confirmar': True
            }
            return render(request, 'neumaticos/cargar_inspecciones.html', context)
        else:
            context = {'errores': errores, 'confirmar': False}
            return render(request, 'neumaticos/cargar_inspecciones.html', context)

    return render(request, 'neumaticos/cargar_inspecciones.html')

@login_required
@user_passes_test(is_admin)
def confirmar_inspecciones(request):
    if request.method == 'POST':
        inspecciones_pendientes = request.session.get('inspecciones_pendientes', [])
        errores = []

        # Agrupar inspecciones por vehículo
        inspecciones_por_vehiculo = {}
        for inspeccion in inspecciones_pendientes:
            key = (inspeccion['cliente'], inspeccion['placa'])
            if key not in inspecciones_por_vehiculo:
                inspecciones_por_vehiculo[key] = []
            inspecciones_por_vehiculo[key].append(inspeccion)

        # Procesar cada vehículo
        for (cliente_email, placa), inspecciones in inspecciones_por_vehiculo.items():
            try:
                cliente = Usuario.objects.get(email=cliente_email)
                vehiculo = Vehiculo.objects.get(placa=placa, usuario=cliente)
            except (Usuario.DoesNotExist, Vehiculo.DoesNotExist) as e:
                errores.append(f"Error al obtener el cliente o vehículo: {str(e)}")
                continue

            # Capturar la fecha anterior de inspección
            fecha_anterior_inspeccion = vehiculo.ultima_inspeccion

            # Guardar los neumáticos actuales en el historial antes de eliminarlos
            for neumatico in vehiculo.neumaticos.all():
                HistorialInspeccion.objects.create(
                    vehiculo=vehiculo,
                    posicion=neumatico.posicion,
                    modelo=neumatico.modelo,
                    marca=neumatico.marca,
                    presion=neumatico.presion,
                    huella=neumatico.huella,
                    dot=neumatico.dot,
                    fecha_inspeccion=fecha_anterior_inspeccion,
                    medida=neumatico.medida.medida if neumatico.medida else 'Desconocida',
                    renovable=neumatico.renovable,
                    precio_estimado=neumatico.precio_estimado,
                    averia=neumatico.averias.first() if neumatico.averias.exists() else None,
                )

            # Eliminar los neumáticos actuales del vehículo
            vehiculo.neumaticos.all().delete()

            # Crear nuevos neumáticos desde el CSV para este vehículo
            for inspeccion_pos in inspecciones:
                try:
                    posicion = inspeccion_pos['posicion']
                    medida = MedidaNeumatico.objects.get(medida=inspeccion_pos['medida'])
                    averia_codigo = inspeccion_pos['averia']

                    # Crear nuevo neumático
                    neumatico = Neumatico.objects.create(
                        vehiculo=vehiculo,
                        posicion=posicion,
                        modelo=inspeccion_pos.get('modelo', 'Desconocido'),
                        marca=inspeccion_pos['marca'],
                        diseño=inspeccion_pos.get('diseño', 'No especificado'),
                        dot=inspeccion_pos['dot'],
                        presion=float(inspeccion_pos['presion']),
                        huella=float(inspeccion_pos['huella']),
                        medida=medida,
                        renovable=inspeccion_pos['renovable'].strip().lower() == 'true',
                        fecha_inspeccion=timezone.now(),
                        precio_estimado=inspeccion_pos.get('precio_estimado', 0.0)
                    )

                    # Asignar averías si existe una avería especificada
                    if averia_codigo:
                        try:
                            averia = Averia.objects.get(codigo=averia_codigo)
                            neumatico.averias.add(averia)
                        except Averia.DoesNotExist:
                            errores.append(f"La avería con código {averia_codigo} no está registrada.")
                    # Si no hay avería especificada, el neumático se guarda sin averías

                    neumatico.save()

                except (MedidaNeumatico.DoesNotExist, ValueError) as e:
                    errores.append(f"Error en la creación del neumático en la posición {posicion} del vehículo con placa {placa}: {str(e)}")
                    continue

            # Actualizar la fecha de última inspección del vehículo
            vehiculo.ultima_inspeccion = timezone.now()
            vehiculo.save()

        if errores:
            context = {'errores': errores}
            return render(request, 'neumaticos/cargar_inspecciones.html', context)

        # Limpiar las inspecciones pendientes de la sesión
        request.session.pop('inspecciones_pendientes', None)
        return redirect('reporte_vehiculos')

    return redirect('cargar_inspecciones')
