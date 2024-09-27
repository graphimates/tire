from django.db import models
from vehiculos.models import Vehiculo
from averias.models import Averia

class Neumatico(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, related_name='neumaticos', on_delete=models.CASCADE)
    posicion = models.IntegerField()  # Posición del neumático en el vehículo
    modelo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    dot = models.CharField(max_length=20)
    presion = models.FloatField()
    huella = models.FloatField()
    averias = models.ManyToManyField(Averia, related_name='neumaticos')  # Relación con las averías

    def __str__(self):
        return f"Neumático en posición {self.posicion} del vehículo {self.vehiculo.placa}"



# models.py dentro de neumaticos
class HistorialInspeccion(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    posicion = models.IntegerField()
    modelo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    dot = models.CharField(max_length=20)
    presion = models.FloatField()
    huella = models.FloatField()
    averias = models.ManyToManyField(Averia)
    fecha_inspeccion = models.DateTimeField()

    def __str__(self):
        return f"Inspección de {self.vehiculo.placa} - Neumático {self.posicion} - {self.fecha_inspeccion}"
