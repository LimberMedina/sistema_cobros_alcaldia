
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/usuarios/",
        include("usuarios.urls")
    ),

    path(
        "api/",
        include("actividades.urls")
    ),

    path(
        "api/documentos/",
        include("documentos.urls")
    ),
]
