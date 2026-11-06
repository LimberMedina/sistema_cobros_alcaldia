
from datetime import date
import calendar
import re

from django.utils import timezone
from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Actividad
from .serializers import ActividadSerializer


class ActividadViewSet(viewsets.ModelViewSet):
    serializer_class = ActividadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Actividad.objects.filter(
            usuario=self.request.user
        )

        mes = self.request.query_params.get("mes")
        anio = self.request.query_params.get("anio")
        fecha = self.request.query_params.get("fecha")

        if mes is not None:
            queryset = queryset.filter(fecha__month=int(mes)) \
                if mes.isdigit() and 1 <= int(mes) <= 12 \
                else queryset.none()

        if anio is not None:
            queryset = queryset.filter(fecha__year=int(anio)) \
                if anio.isdigit() and 1 <= int(anio) <= 9999 \
                else queryset.none()

        if fecha:
            queryset = queryset.filter(fecha=fecha)

        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ActividadVozView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        texto = request.data.get("texto", "")
        fecha = request.data.get("fecha")

        if not isinstance(texto, str) or not texto.strip():
            return Response(
                {"error": "Debes proporcionar una actividad."},
                status=status.HTTP_400_BAD_REQUEST
            )

        texto = texto.strip()

        # El cliente puede enviar la fecha seleccionada.
        # Si no la envía, se interpreta el texto.
        if fecha:
            try:
                fecha_actividad = date.fromisoformat(fecha)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Fecha inválida. Usa YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            hoy = timezone.localdate()

            # Detectar fechas dictadas: 05/11/2026 o 5-11-2026
            patron = (
                r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b"
            )
            resultado = re.search(patron, texto)

            if resultado:
                dia, mes, anio = map(int, resultado.groups())

                try:
                    fecha_actividad = date(anio, mes, dia)
                except ValueError:
                    return Response(
                        {"error": "La fecha dictada no es válida."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                texto = (
                    texto[:resultado.start()] +
                    texto[resultado.end():]
                ).strip()

            elif re.search(r"\bayer\b", texto, re.IGNORECASE):
                from datetime import timedelta
                fecha_actividad = hoy - timedelta(days=1)

            elif re.search(r"\bhoy\b", texto, re.IGNORECASE):
                fecha_actividad = hoy

            else:
                return Response(
                    {
                        "error": (
                            "Indica una fecha explícita, "
                            "di hoy/ayer o envía el campo fecha."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Eliminar comandos iniciales habituales
        texto = re.sub(
            r"^(agregar|registrar|guardar)\s+"
            r"(una\s+)?actividad\s*(para|del|de)?\s*",
            "",
            texto,
            flags=re.IGNORECASE
        )

        # Retirar la expresión de fecha del texto.
        texto = re.sub(
            r"^(el\s+)?\d{1,2}[/-]\d{1,2}[/-]\d{4}\s*",
            "",
            texto
        )

        texto = re.sub(
            r"^(para\s+)?(hoy|ayer)\s*",
            "",
            texto,
            flags=re.IGNORECASE
        )

        texto = texto.lstrip(" :,-.")

        if not texto:
            return Response(
                {"error": "No se encontró una descripción."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ActividadSerializer(data={
            "fecha": fecha_actividad.isoformat(),
            "descripcion": texto
        })

        serializer.is_valid(raise_exception=True)
        actividad = serializer.save(usuario=request.user)

        return Response(
            {
                "mensaje": "Actividad registrada correctamente.",
                "actividad": ActividadSerializer(actividad).data
            },
            status=status.HTTP_201_CREATED
        )


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hoy = timezone.localdate()

        try:
            mes = int(request.query_params.get("mes", hoy.month))
            anio = int(request.query_params.get("anio", hoy.year))

            if not 1 <= mes <= 12 or not 1 <= anio <= 9999:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {"error": "Mes o año inválidos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        actividades = Actividad.objects.filter(
            usuario=request.user,
            fecha__year=anio,
            fecha__month=mes
        )

        dias = actividades.values("fecha").annotate(
            total=Count("id")
        )

        ultimo_dia = calendar.monthrange(anio, mes)[1]

        return Response({
            "mes": mes,
            "anio": anio,
            "total_actividades": actividades.count(),
            "dias_con_actividades": dias.count(),
            "dias_del_mes": ultimo_dia,
            "actividades_recientes": ActividadSerializer(
                actividades.order_by("-fecha", "-id")[:5],
                many=True
            ).data
        })
