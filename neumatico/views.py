from django.shortcuts import render, get_object_or_404, redirect
from .models import Neumatico
from vehiculos.models import Vehiculo
from .forms import NeumaticoForm

def crear_neumatico(request, vehiculo_id, posicion):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    if request.method == 'POST':
        form = NeumaticoForm(request.POST)
        if form.is_valid():
            neumatico = form.save(commit=False)
            neumatico.vehiculo = vehiculo
            neumatico.posicion = posicion
            neumatico.save()
            form.save_m2m()  # Guardar las averías seleccionadas
            return redirect('ver_vehiculo', vehiculo_id=vehiculo.id)
    else:
        form = NeumaticoForm(initial={'posicion': posicion})

    return render(request, 'neumaticos/crear_neumatico.html', {'form': form, 'vehiculo': vehiculo, 'posicion': posicion})
