from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:vehiculo_id>/<int:posicion>/', views.crear_neumatico, name='crear_neumatico'),
]
