from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:user_id>/', views.crear_vehiculo, name='crear_vehiculo'),    
]
