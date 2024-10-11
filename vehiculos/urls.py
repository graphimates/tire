from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:user_id>/', views.crear_vehiculo, name='crear_vehiculo'),    
    path('reporte/', views.reporte_vehiculos, name='reporte_vehiculos'),  # Nueva ruta para el reporte de vehículos
    path('borrar/<int:vehiculo_id>/', views.borrar_vehiculo, name='borrar_vehiculo'),  # Asegúrate de que esta ruta esté definida
    path('editar_fecha_inspeccion/<int:vehiculo_id>/', views.editar_fecha_inspeccion, name='editar_fecha_inspeccion'),

]
