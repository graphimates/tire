from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:user_id>/', views.crear_vehiculo, name='crear_vehiculo'),    
    path('reporte/', views.reporte_vehiculos, name='reporte_vehiculos'),  # Nueva ruta para el reporte de vehículos
]
