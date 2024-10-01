# neumatico/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Neumatico, HistorialInspeccion, MedidaNeumatico
from vehiculos.models import Vehiculo
from .forms import NeumaticoForm, MedidaForm
from django.utils import timezone
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

@login_required
@user_passes_test(is_admin)
def eliminar_medida(request, medida_id):
    medida = get_object_or_404(MedidaNeumatico, id=medida_id)
    if request.method == 'POST':
        medida.delete()
        return redirect('ver_medidas')
    
    return render(request, 'medidas/eliminar_medida.html', {'medida': medida})


# views.py
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
                medida=neumatico.medida,
                renovable=neumatico.renovable,
                precio_estimado=neumatico.precio_estimado,
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

                # Obtener el precio estimado de la medida
                neumatico.actualizar_precio()
                neumatico.save()

                # Si alguna de las averías es de montura, marcar como no operativo
                for averia in form.cleaned_data['averias']:
                    if averia.servicio_requerido == 'montura':
                        neumatico.renovable = False

                # Guardar las averías
                form.save_m2m()
            else:
                valid_forms = False
                print(f"Formulario de posición {posicion} no es válido: {form.errors}")

        if valid_forms:
            # Actualizar la fecha de última inspección
            vehiculo.ultima_inspeccion = timezone.now()
            vehiculo.save()
            return redirect('reporte_vehiculos')

    # Crear un formulario para cada neumático
    forms = [NeumaticoForm(prefix=f'neumatico_{posicion}') for posicion in range(1, vehiculo.cantidad_neumaticos + 1)]
    return render(request, 'neumaticos/crear_neumatico.html', {'forms': forms, 'vehiculo': vehiculo})




def ver_neumaticos(request):
    neumaticos = Neumatico.objects.select_related('vehiculo').all()
    return render(request, 'neumaticos/ver_neumaticos.html', {'neumaticos': neumaticos})