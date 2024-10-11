# Generated by Django 4.2.7 on 2024-10-11 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('averias', '0003_alter_averia_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='averia',
            name='criticidad',
            field=models.CharField(choices=[('bajo', 'Bajo'), ('moderado', 'Moderado'), ('alto', 'Alto')], default='bajo', max_length=20),
        ),
    ]
