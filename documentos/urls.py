
from django.urls import path

from .views import (
    SolicitudDescargarView,
    InformeDescargarView,
    PeriodosDisponiblesView,
    HistorialDocumentosView,
)

urlpatterns = [
    path(
        "periodos/",
        PeriodosDisponiblesView.as_view()
    ),
    path(
        "solicitud/",
        SolicitudDescargarView.as_view()
    ),
    path(
        "informe/",
        InformeDescargarView.as_view()
    ),
    path(
        "historial/",
        HistorialDocumentosView.as_view()
    ),
]
