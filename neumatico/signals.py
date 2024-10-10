# neumatico/signals.py
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Neumatico

@receiver(m2m_changed, sender=Neumatico.averias.through)
def actualizar_renovable(sender, instance, **kwargs):
    if any(averia.estado == 'no_operativo' for averia in instance.averias.all()):
        if instance.renovable != False:
            instance.renovable = False
            instance.save(update_fields=['renovable'])
