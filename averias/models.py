from django.db import models

class Averia(models.Model):
    ESTADOS_NEUMATICO = [
        ('operativo', 'Operativo'),
        ('renovable', 'Renovable'),
        ('desperdicio', 'Desperdicio'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    estado_neumatico = models.CharField(max_length=20, choices=ESTADOS_NEUMATICO)

    def __str__(self):
        return f"{self.nombre} - {self.estado_neumatico}"
