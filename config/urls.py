
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

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

    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
