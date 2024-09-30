from django.urls import path
from . import views

urlpatterns = [
    path('', views.ver_averias, name='ver_averias'),  # Ruta para ver todas las averías
    path('crear/', views.crear_averia, name='crear_averia'),  # Ruta para crear una avería
    path('editar/<int:averia_id>/', views.editar_averia, name='editar_averia'),  # Ruta para editar una avería
    path('eliminar/<int:averia_id>/', views.eliminar_averia, name='eliminar_averia'),  # Ruta para eliminar una avería
]
