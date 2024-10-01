# averias/models.py
from django.db import models

class Averia(models.Model):
    SERVICIOS_REPARACION = [
        ('alineacion', 'Alineación'),
        ('montura', 'Montura'),
        ('balanceo', 'Balanceo'),
        ('calibracion', 'Calibración'),
        ('rotacion', 'Rotación'),
    ]

    nombre = models.CharField(max_length=100)
    servicio_requerido = models.CharField(max_length=20, choices=SERVICIOS_REPARACION)

    def __str__(self):
        return f"{self.nombre} - {self.get_servicio_requerido_display()}"
