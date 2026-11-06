
from django.urls import path

from .views import (
    SolicitudDescargarView,
    InformeDescargarView,
)

urlpatterns = [
    path(
        "solicitud/",
        SolicitudDescargarView.as_view()
    ),
    path(
        "informe/",
        InformeDescargarView.as_view()
    ),
]
