
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Perfil
from .serializers import LoginSerializer, RegistroSerializer, PerfilSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer



class RegistroView(generics.CreateAPIView):

    serializer_class = RegistroSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        usuario = serializer.save()

        return Response(
            {
                "mensaje": "Usuario registrado correctamente.",
                "usuario": {
                    "id": usuario.id,
                    "username": usuario.username,
                    "email": usuario.email,
                    "nombre_completo": (
                        usuario.perfil.nombre_completo
                    )
                }
            },
            status=201
        )


class PerfilView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def obtener_perfil(self, usuario):
        perfil, _ = Perfil.objects.get_or_create(
            usuario=usuario,
            defaults={
                "nombre_completo": (
                    usuario.get_full_name() or usuario.username
                )
            }
        )
        return perfil

    def get(self, request):
        perfil = self.obtener_perfil(request.user)
        serializer = PerfilSerializer(perfil)
        return Response(serializer.data)

    def put(self, request):
        perfil = self.obtener_perfil(request.user)

        serializer = PerfilSerializer(
            perfil,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def patch(self, request):
        return self.put(request)
