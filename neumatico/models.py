from django.db import models
from vehiculos.models import Vehiculo
from averias.models import Averia

class MedidaNeumatico(models.Model):
    medida = models.CharField(max_length=20, unique=True)  # Medida del neumático (por ejemplo, "185/65R15")
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2)  # Precio relacionado con la medida

    def __str__(self):
        return f"{self.medida} - ${self.precio_estimado}"

# models.py de Neumatico
class Neumatico(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, related_name='neumaticos', on_delete=models.CASCADE)
    posicion = models.IntegerField()  # Posición del neumático en el vehículo
    modelo = models.CharField(max_length=50)  # El modelo debería estar aquí
    marca = models.CharField(max_length=50)
    diseño = models.CharField(max_length=50)  # Nuevo campo para el diseño
    dot = models.CharField(max_length=20)
    presion = models.FloatField()
    huella = models.FloatField()
    medida = models.ForeignKey('MedidaNeumatico', on_delete=models.SET_NULL, null=True)  # Relacionado con medida
    averias = models.ManyToManyField(Averia, related_name='neumaticos')  # Relación con las averías
    renovable = models.BooleanField(default=True)  # Campo para si es renovable
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Precio estimado

    def actualizar_precio(self):
        """Método para actualizar el precio basado en la medida seleccionada"""
        if self.medida:
            self.precio_estimado = self.medida.precio_estimado

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
    fecha_inspeccion = models.DateTimeField()
    medida = models.CharField(max_length=50)  # Nuevo campo para la medida
    renovable = models.BooleanField(default=True)  # Nuevo campo para si es renovable o no
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2)  # Nuevo campo para precio estimado

    def __str__(self):
        return f"Inspección de {self.vehiculo.placa} - Neumático {self.posicion} - {self.fecha_inspeccion}"

