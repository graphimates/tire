# Generated by Django 4.2.7 on 2024-10-09 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('neumatico', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='neumatico',
            name='medida',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='neumatico.medidaneumatico'),
        ),
        migrations.AlterField(
            model_name='neumatico',
            name='modelo',
            field=models.CharField(blank=True, choices=[('direccional', 'Direccional'), ('traccion', 'Tracción'), ('all position', 'All Position')], max_length=20),
        ),
    ]
