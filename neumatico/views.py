# neumatico/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Neumatico, HistorialInspeccion
from vehiculos.models import Vehiculo
from .forms import NeumaticoForm
from django.utils import timezone


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
            )

        # Eliminar los neumáticos actuales para reemplazarlos con los nuevos datos
        vehiculo.neumaticos.all().delete()

        # Procesar los formularios de nuevos neumáticos
        for posicion in range(1, vehiculo.cantidad_neumaticos + 1):
            form = NeumaticoForm(request.POST, prefix=f'neumatico_{posicion}')

            # Asignar la posición manualmente si no se envía desde el formulario
            if not form.data.get(f'neumatico_{posicion}-posicion'):
                form.data = form.data.copy()
                form.data[f'neumatico_{posicion}-posicion'] = posicion

            if form.is_valid():
                neumatico = form.save(commit=False)
                neumatico.vehiculo = vehiculo
                neumatico.posicion = posicion
                neumatico.save()

                # Guardar las averías después de guardar el neumático
                form.save_m2m()  # Esto guarda las relaciones de muchos a muchos como las averías
            else:
                valid_forms = False
                print(f"Formulario de posición {posicion} no es válido: {form.errors}")

        if valid_forms:
            # Actualizar la fecha de última inspección
            vehiculo.ultima_inspeccion = timezone.now()
            vehiculo.save()
            return redirect('reporte_vehiculos')  # Redirigir al reporte de vehículos

    # Crear un formulario para cada neumático
    forms = [NeumaticoForm(prefix=f'neumatico_{posicion}') for posicion in range(1, vehiculo.cantidad_neumaticos + 1)]
    return render(request, 'neumaticos/crear_neumatico.html', {'forms': forms, 'vehiculo': vehiculo})


def ver_neumaticos(request):
    neumaticos = Neumatico.objects.select_related('vehiculo').all()
    return render(request, 'neumaticos/ver_neumaticos.html', {'neumaticos': neumaticos})