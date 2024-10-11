# averias/models.py
from django.db import models

# averias/models.py
class Averia(models.Model):
    ESTADO_OPCIONES = [
        ('operativo', 'Operativo'),
        ('no_operativo', 'No operativo')
    ]
    
    SERVICIOS_REPARACION = [
        ('alineacion', 'Alineación'),
        ('montura', 'Montura'),
        ('balanceo', 'Balanceo'),
        ('calibracion', 'Calibración'),
        ('rotacion', 'Rotación'),
    ]

    CRITICIDAD_OPCIONES = [
        ('bajo', 'Bajo'),
        ('moderado', 'Moderado'),
        ('alto', 'Alto'),
    ]

    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    servicio_requerido = models.CharField(max_length=20, choices=SERVICIOS_REPARACION)
    estado = models.CharField(max_length=20, choices=ESTADO_OPCIONES, default='no_operativo')
    criticidad = models.CharField(max_length=20, choices=CRITICIDAD_OPCIONES, default='bajo')  # Nuevo campo

    def __str__(self):
        return f"{self.nombre} ({self.codigo}) - {self.get_servicio_requerido_display()}"
