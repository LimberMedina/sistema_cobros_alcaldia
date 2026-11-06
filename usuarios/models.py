
from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    nombre_completo = models.CharField(max_length=200)
    cargo = models.CharField(max_length=200, blank=True)

    institucion = models.CharField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=120, default="Cuatro Cañadas")

    destinatario = models.CharField(max_length=200, blank=True)
    cargo_destinatario = models.CharField(max_length=200, blank=True)

    via_1 = models.CharField(max_length=200, blank=True)
    cargo_via_1 = models.CharField(max_length=200, blank=True)

    via_2 = models.CharField(max_length=200, blank=True)
    cargo_via_2 = models.CharField(max_length=200, blank=True)

    numero_instructivo = models.CharField(
        max_length=50,
        default="004/2026"
    )

    def __str__(self):
        return self.nombre_completo
