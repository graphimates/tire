# Generated by Django 4.2.7 on 2024-10-18 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='profile_photo',
            field=models.ImageField(blank=True, default='profile_photos/default-profile.png', null=True, upload_to='profile_photos/'),
        ),
    ]
