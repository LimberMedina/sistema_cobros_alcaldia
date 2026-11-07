from django.db import models
from django.contrib.auth.models import User


class DocumentoGenerado(models.Model):
    TIPOS = (
        ("solicitud", "Solicitud de pago"),
        ("informe", "Informe mensual"),
    )
    FORMATOS = (
        ("pdf", "PDF"),
        ("docx", "Word"),
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documentos_generados",
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveIntegerField()
    formato = models.CharField(max_length=4, choices=FORMATOS)
    fecha_emision = models.DateField(null=True, blank=True)
    incluir_fotos = models.BooleanField(default=False)
    generado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generado_en", "-id"]
        indexes = [
            models.Index(fields=["usuario", "-generado_en"]),
        ]
