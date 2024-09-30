from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:vehiculo_id>/', views.crear_neumatico, name='crear_neumatico'),
    path('ver_neumaticos/', views.ver_neumaticos, name='ver_neumaticos'),


]
