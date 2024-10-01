from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:vehiculo_id>/', views.crear_neumatico, name='crear_neumatico'),
     path('ver_neumaticos/', views.ver_neumaticos, name='ver_neumaticos'),
     path('medidas/', views.ver_medidas, name='ver_medidas'),
    path('medidas/crear/', views.crear_medida, name='crear_medida'),
    path('medidas/editar/<int:medida_id>/', views.editar_medida, name='editar_medida'),  # Ruta para editar
    path('medidas/eliminar/<int:medida_id>/', views.eliminar_medida, name='eliminar_medida'),  # Ruta para eliminar

]
