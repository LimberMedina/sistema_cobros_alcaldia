
from django.db import models
from django.contrib.auth.models import User


class Actividad(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="actividades"
    )

    fecha = models.DateField()

    descripcion = models.TextField()

    imagen = models.ImageField(
        upload_to="actividades/",
        blank=True,
        null=True,
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha", "creado_en", "id"]
        indexes = [
            models.Index(fields=["usuario", "fecha"])
        ]

    def __str__(self):
        return f"{self.fecha} - {self.descripcion[:50]}"
