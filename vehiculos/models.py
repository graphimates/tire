# vehiculos/models.py
from django.db import models
from usuarios.models import Usuario

# vehiculos/models.py
class Vehiculo(models.Model):
    TIPOS_VEHICULOS = [
        ('2x2', 'Vehículo 2x2'),
        ('4x2', 'Vehículo 4x2'),
        ('4x2L', 'Vehículo 4x2L'),
        ('6x2', 'Vehículo 6x2'),
        ('6x2M', 'Vehículo 6x2M'),
        ('6x4', 'Vehículo 6x4'),
        ('T4x0', 'Vehículo T4x0'),
        ('T6x0', 'Vehículo T6x0'),
    ]
    
    usuario = models.ForeignKey(Usuario, related_name='vehiculos', on_delete=models.CASCADE)
    placa = models.CharField(max_length=20)
    modelo = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPOS_VEHICULOS)
    ultima_inspeccion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.placa} - {self.modelo}"

    @property
    def cantidad_neumaticos(self):
        # Extrae el número inicial del tipo de vehículo (e.g., '2x2' devolverá 2)
        return int(self.tipo[0]) * 2  # Por ejemplo, 2x2 = 4 neumáticos