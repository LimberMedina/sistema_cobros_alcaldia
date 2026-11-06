
from django.urls import path

from .views import (
    SolicitudDescargarView,
    InformeDescargarView,
    PeriodosDisponiblesView,
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
]
