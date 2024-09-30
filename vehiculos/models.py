# vehiculos/models.py
from django.db import models
from usuarios.models import Usuario

class Vehiculo(models.Model):
    TIPOS_VEHICULOS = [
        (2, '2 Neumáticos'),
        (4, '4 Neumáticos'),
        (6, '6 Neumáticos'),
        (16, '16 Neumáticos')
    ]
    
    usuario = models.ForeignKey(Usuario, related_name='vehiculos', on_delete=models.CASCADE)
    placa = models.CharField(max_length=20)
    modelo = models.CharField(max_length=50)
    tipo = models.IntegerField(choices=TIPOS_VEHICULOS)
    ultima_inspeccion = models.DateTimeField(null=True, blank=True)  # Nueva variable para la fecha de inspección

    def __str__(self):
        return f"{self.placa} - {self.modelo}"

    @property
    def tiene_neumaticos(self):
        return self.neumaticos.count() > 0
