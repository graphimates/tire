# neumatico/models.py

from django.core.exceptions import ValidationError
from django.db import models
from vehiculos.models import Vehiculo
from averias.models import Averia
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone

# Medida de neumático con su precio estimado
class MedidaNeumatico(models.Model):
    medida = models.CharField(max_length=20, unique=True)
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.medida} - ${self.precio_estimado}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for neumatico in self.neumatico_set.all():
            neumatico.precio_estimado = self.precio_estimado
            neumatico.save()

# Neumático vinculado a un vehículo
class Neumatico(models.Model):
    MODELO_CHOICES = [
        ('direccional', 'Direccional'),
        ('traccion', 'Tracción'),
        ('all position', 'All Position'),
    ]

    vehiculo = models.ForeignKey(Vehiculo, related_name='neumaticos', on_delete=models.CASCADE)
    posicion = models.IntegerField()
    modelo = models.CharField(max_length=20, choices=MODELO_CHOICES, blank=True)
    marca = models.CharField(max_length=50)
    diseño = models.CharField(max_length=50)
    dot = models.CharField(max_length=20)
    presion = models.FloatField()
    huella = models.FloatField()
    medida = models.ForeignKey('MedidaNeumatico', on_delete=models.SET_NULL, null=True, blank=True)
    renovable = models.BooleanField(default=False)
    averias = models.ManyToManyField(Averia, related_name='neumaticos')
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_inspeccion = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if not self.dot:
            raise ValidationError({'dot': 'El campo DOT es obligatorio.'})
        if self.huella < 0:
            raise ValidationError({'huella': 'La huella no puede ser menor a 0. Puede ser 0, pero no negativa.'})

    def actualizar_precio(self):
        if self.medida:
            self.precio_estimado = self.medida.precio_estimado
        else:
            self.precio_estimado = 0.0

    def save(self, *args, **kwargs):
        # Actualizar precio antes de guardar
        self.actualizar_precio()

        # Validar que el precio estimado no sea nulo solo si hay medida
        if self.medida and self.precio_estimado is None:
            raise ValidationError("El precio estimado no puede ser nulo.")

        # Guardar el objeto
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Neumático en posición {self.posicion} del vehículo {self.vehiculo.placa}"

# Historial de inspección del neumático
class HistorialInspeccion(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    posicion = models.IntegerField()
    modelo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    dot = models.CharField(max_length=20)
    presion = models.FloatField()
    huella = models.FloatField()
    fecha_inspeccion = models.DateTimeField()
    medida = models.CharField(max_length=50)
    renovable = models.BooleanField(default=True)
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2)
    averia = models.ForeignKey(Averia, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Inspección de {self.vehiculo.placa} - Neumático {self.posicion} - {self.fecha_inspeccion}"

# Señal para actualizar el campo renovable basado en las averías
@receiver(m2m_changed, sender=Neumatico.averias.through)
def actualizar_renovable(sender, instance, **kwargs):
    if any(averia.estado == 'no_operativo' for averia in instance.averias.all()):
        if instance.renovable != False:
            instance.renovable = False
            instance.save(update_fields=['renovable'])
