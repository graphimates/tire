from django.urls import path
from . import views

urlpatterns = [
  
    path('ver_neumaticos/', views.ver_neumaticos, name='ver_neumaticos'),
    path('medidas/', views.ver_medidas, name='ver_medidas'),
    path('medidas/crear/', views.crear_medida, name='crear_medida'),
    path('medidas/editar/<int:medida_id>/', views.editar_medida, name='editar_medida'),  # Ruta para editar
    path('medidas/eliminar/<int:medida_id>/', views.eliminar_medida, name='eliminar_medida'),  # Ruta para eliminar
    path('historico_datos/<int:user_id>/', views.historico_datos, name='historico_datos'),
    path('cargar_inspecciones/', views.cargar_inspecciones, name='cargar_inspecciones'),
    path('confirmar_inspecciones/', views.confirmar_inspecciones, name='confirmar_inspecciones'),
    
     path('neumaticos/editar/<int:vehiculo_id>/<int:posicion>/', views.editar_neumatico, name='editar_neumatico'),


]
