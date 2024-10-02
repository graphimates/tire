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
    codigo = models.CharField(max_length=10, unique=True)  # Nuevo campo para el código
    servicio_requerido = models.CharField(max_length=20, choices=SERVICIOS_REPARACION)

    def __str__(self):
        return f"{self.nombre} ({self.codigo}) - {self.get_servicio_requerido_display()}"

    @property
    def es_no_operativo(self):
        # Si el servicio relacionado es 'montura', se considera que el neumático es no operativo
        return self.servicio_requerido == 'montura'