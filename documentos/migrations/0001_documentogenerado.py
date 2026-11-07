from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentoGenerado",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("solicitud", "Solicitud de pago"),
                            ("informe", "Informe mensual"),
                        ],
                        max_length=20,
                    ),
                ),
                ("mes", models.PositiveSmallIntegerField()),
                ("anio", models.PositiveIntegerField()),
                (
                    "formato",
                    models.CharField(
                        choices=[("pdf", "PDF"), ("docx", "Word")],
                        max_length=4,
                    ),
                ),
                ("fecha_emision", models.DateField(blank=True, null=True)),
                ("incluir_fotos", models.BooleanField(default=False)),
                ("generado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documentos_generados",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-generado_en", "-id"],
                "indexes": [
                    models.Index(
                        fields=["usuario", "-generado_en"],
                        name="documentos__usuario_854a1d_idx",
                    )
                ],
            },
        ),
    ]
