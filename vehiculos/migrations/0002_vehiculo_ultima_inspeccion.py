# Generated by Django 5.1.1 on 2024-09-26 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='ultima_inspeccion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
