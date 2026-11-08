
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ActividadViewSet,
    ActividadImagenView,
    ActividadVozView,
    DashboardView,
)

router = DefaultRouter()
router.register(
    "actividades",
    ActividadViewSet,
    basename="actividad"
)

urlpatterns = [
    path("actividades/voz/", ActividadVozView.as_view()),
    path(
        "actividades/<int:pk>/imagen/",
        ActividadImagenView.as_view(),
        name="actividad-imagen",
    ),
    path("dashboard/", DashboardView.as_view()),
    path("", include(router.urls)),
]
