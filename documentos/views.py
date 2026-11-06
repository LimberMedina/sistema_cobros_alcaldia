
from datetime import date

from django.http import FileResponse
from django.utils import timezone
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from usuarios.models import Perfil
from actividades.models import Actividad

from .generadores import (
    carta_word,
    carta_pdf,
    informe_word,
    informe_pdf,
)


def parametros_periodo(request):
    hoy = timezone.localdate()

    try:
        mes = int(request.query_params.get("mes", hoy.month))
        anio = int(request.query_params.get("anio", hoy.year))

        if not 1 <= mes <= 12 or not 1 <= anio <= 9999:
            raise ValueError
    except (ValueError, TypeError):
        raise ValidationError(
            {"periodo": "Mes o año inválido."}
        )

    formato = request.query_params.get(
        "formato", "pdf"
    ).lower()

    if formato not in ("pdf", "docx"):
        raise ValidationError(
            {"formato": "Usa pdf o docx."}
        )

    return mes, anio, formato


def obtener_perfil(request):
    try:
        perfil = Perfil.objects.get(usuario=request.user)
    except Perfil.DoesNotExist:
        raise ValidationError({
            "perfil": "Debes completar tu perfil."
        })

    if not perfil.nombre_completo.strip() or not perfil.cargo.strip():
        raise ValidationError({
            "perfil": "Debes configurar tu nombre y cargo."
        })

    return perfil


def respuesta_archivo(buffer, nombre, formato):
    tipo = (
        "application/pdf"
        if formato == "pdf"
        else (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=nombre,
        content_type=tipo
    )


class SolicitudDescargarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mes, anio, formato = parametros_periodo(request)
        perfil = obtener_perfil(request)

        fecha_texto = request.query_params.get("fecha")
        desde_texto = request.query_params.get("desde")
        hasta_texto = request.query_params.get("hasta")

        try:
            fecha = (
                date.fromisoformat(fecha_texto)
                if fecha_texto
                else timezone.localdate()
            )

            desde = (
                date.fromisoformat(desde_texto)
                if desde_texto
                else None
            )

            hasta = (
                date.fromisoformat(hasta_texto)
                if hasta_texto
                else None
            )
        except ValueError:
            raise ValidationError({
                "fecha": "Las fechas deben estar en formato YYYY-MM-DD."
            })

        if bool(desde) != bool(hasta):
            raise ValidationError({
                "periodo": "Debes indicar desde y hasta juntos."
            })

        if desde and hasta:
            if desde > hasta:
                raise ValidationError({
                    "periodo": "La fecha inicial es posterior a la final."
                })

            if (
                desde.year != anio or hasta.year != anio
                or desde.month != mes or hasta.month != mes
            ):
                raise ValidationError({
                    "periodo": "El rango debe pertenecer al mes solicitado."
                })

        if formato == "pdf":
            archivo = carta_pdf(
                perfil, mes, anio, fecha, desde, hasta
            )
        else:
            archivo = carta_word(
                perfil, mes, anio, fecha, desde, hasta
            )

        nombre = f"solicitud_{anio}_{mes:02d}.{formato}"

        return respuesta_archivo(archivo, nombre, formato)


class InformeDescargarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mes, anio, formato = parametros_periodo(request)
        perfil = obtener_perfil(request)

        actividades = list(
            Actividad.objects.filter(
                usuario=request.user,
                fecha__month=mes,
                fecha__year=anio
            ).order_by("fecha", "creado_en", "id")
        )

        if formato == "pdf":
            archivo = informe_pdf(
                perfil, mes, anio, actividades
            )
        else:
            archivo = informe_word(
                perfil, mes, anio, actividades
            )

        nombre = f"informe_{anio}_{mes:02d}.{formato}"

        return respuesta_archivo(archivo, nombre, formato)


class PeriodosDisponiblesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        periodos = (
            Actividad.objects.filter(usuario=request.user)
            .annotate(
                mes=ExtractMonth("fecha"),
                anio=ExtractYear("fecha"),
            )
            .values("mes", "anio")
            .annotate(total=Count("id"))
            .order_by("-anio", "-mes")
        )

        hoy = timezone.localdate()
        disponibles = [
            {"mes": hoy.month, "anio": hoy.year, "total": 0}
        ]
        vistos = {(hoy.month, hoy.year)}

        for periodo in periodos:
            clave = (periodo["mes"], periodo["anio"])
            if clave in vistos:
                for item in disponibles:
                    if (item["mes"], item["anio"]) == clave:
                        item["total"] = periodo["total"]
                        break
                continue

            vistos.add(clave)
            disponibles.append({
                "mes": periodo["mes"],
                "anio": periodo["anio"],
                "total": periodo["total"],
            })

        return Response(disponibles)
