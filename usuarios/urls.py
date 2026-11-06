
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, RegistroView, PerfilView

urlpatterns = [
    path("registro/", RegistroView.as_view()),
    path("login/", LoginView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("perfil/", PerfilView.as_view()),
]
