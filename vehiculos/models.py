from django.db import models
from usuarios.models import Usuario

class Vehiculo(models.Model):
    TIPOS_VEHICULOS = [
        (2, '2 Neumáticos'),
        (3, '3 Neumáticos'),
        (4, '4 Neumáticos'),
        (16, '16 Neumáticos'),
    ]

    usuario = models.ForeignKey(Usuario, related_name='vehiculos', on_delete=models.CASCADE)
    placa = models.CharField(max_length=20)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    tipo = models.IntegerField(choices=TIPOS_VEHICULOS)

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa}) - Dueño: {self.usuario.first_name} {self.usuario.last_name}, Empresa: {self.usuario.empresa}, Correo: {self.usuario.email}"

