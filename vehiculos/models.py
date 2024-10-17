from django.db import models
from usuarios.models import Usuario

class Vehiculo(models.Model):
    TIPOS_VEHICULOS = [
        ('4x2LT', 'Vehículo 4x2LT'),
        ('4x2', 'Vehículo 4x2'),
        ('4x2L', 'Vehículo 4x2L'),
        ('6x2', 'Vehículo 6x2'),
        ('6x2M', 'Vehículo 6x2M'),
        ('6x4', 'Vehículo 6x4'),
        ('T2x0', 'Vehículo T2x0'),
        ('T4x0', 'Vehículo T4x0'),
        ('T6x0', 'Vehículo T6x0'),
        ('TT6x0', 'Vehículo TT6x0'),

    ]
    
    usuario = models.ForeignKey(Usuario, related_name='vehiculos', on_delete=models.CASCADE)
    placa = models.CharField(max_length=20, unique=True)  # Add unique=True
    modelo = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPOS_VEHICULOS)
    ultima_inspeccion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.placa} - {self.modelo}"

    @property
    def cantidad_neumaticos(self):
        # Definir la cantidad de neumáticos según el tipo de vehículo
        cantidad_por_tipo = {
            '4x2LT': 4,
            '4x2': 6,
            '4x2L': 6,
            '6x2': 10,
            '6x2M': 10,
            '6x4': 10,
            'T2x0': 4,
            'T4x0': 8,
            'T6x0': 12,  # Aquí especificamos que el tipo T6x0 tiene 12 neumáticos
            'TT6x0': 12,

        }
        return cantidad_por_tipo.get(self.tipo, 4)  # Valor por defecto si el tipo no existe
