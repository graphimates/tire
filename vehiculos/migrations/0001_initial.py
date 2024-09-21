# Generated by Django 5.1.1 on 2024-09-21 22:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placa', models.CharField(max_length=20)),
                ('marca', models.CharField(max_length=50)),
                ('modelo', models.CharField(max_length=50)),
                ('tipo', models.IntegerField(choices=[(2, '2 Neumáticos'), (3, '3 Neumáticos'), (4, '4 Neumáticos'), (16, '16 Neumáticos')])),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehiculos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
