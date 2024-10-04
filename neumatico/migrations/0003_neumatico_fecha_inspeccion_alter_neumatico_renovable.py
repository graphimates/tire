# Generated by Django 4.2.7 on 2024-10-04 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neumatico', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='neumatico',
            name='fecha_inspeccion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='neumatico',
            name='renovable',
            field=models.BooleanField(default=False),
        ),
    ]
