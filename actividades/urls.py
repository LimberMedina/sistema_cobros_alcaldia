
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ActividadViewSet,
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
    path("dashboard/", DashboardView.as_view()),
    path("", include(router.urls)),
]
