# Generated by Django 4.2.16 on 2024-09-30 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculos', '0002_vehiculo_ultima_inspeccion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiculo',
            name='tipo',
            field=models.CharField(choices=[('2x2', 'Vehículo 2x2'), ('4x2', 'Vehículo 4x2'), ('4x2L', 'Vehículo 4x2L'), ('6x2', 'Vehículo 6x2'), ('6x2M', 'Vehículo 6x2M'), ('6x4', 'Vehículo 6x4'), ('T4x0', 'Vehículo T4x0'), ('T6x0', 'Vehículo T6x0')], max_length=20),
        ),
    ]
