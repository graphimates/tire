from django.db import models
from usuarios.models import Usuario

class Vehiculo(models.Model):
    MODELOS_VEHICULOS = [
        ('moto', 'Moto'),
        ('auto', 'Auto'),
        ('camion', 'Camión'),
        # Puedes agregar más modelos según el tipo de vehículos que administre el negocio
    ]
    
    usuario = models.ForeignKey(Usuario, related_name='vehiculos', on_delete=models.CASCADE)
    modelo = models.CharField(max_length=20, choices=MODELOS_VEHICULOS)
    cantidad_neumaticos = models.IntegerField()

    def __str__(self):
        return f"{self.modelo} - {self.cantidad_neumaticos} neumáticos"

class Neumatico(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, related_name='neumaticos', on_delete=models.CASCADE)
    posicion = models.IntegerField()  # Ejemplo: Posición 1, 2, 3, etc.

    def __str__(self):
        return f"Neumático en posición {self.posicion} del {self.vehiculo.modelo}"
