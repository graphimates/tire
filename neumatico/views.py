# neumatico/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Neumatico, HistorialInspeccion, MedidaNeumatico
from vehiculos.models import Vehiculo
from usuarios.models import Usuario
from .forms import NeumaticoForm, MedidaForm
from django.utils import timezone
from collections import Counter
from django.contrib.auth.decorators import login_required, user_passes_test


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


# Vista para crear neumático
@login_required
@user_passes_test(lambda u: u.is_superuser)
def crear_neumatico(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    
    if request.method == 'POST':
        valid_forms = True

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
                fecha_inspeccion=timezone.now(),
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

        if valid_forms:
            vehiculo.ultima_inspeccion = timezone.now()
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
