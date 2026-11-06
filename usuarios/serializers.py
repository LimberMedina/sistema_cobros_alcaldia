
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Perfil


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        identificador = attrs.get("username", "").strip()

        if "@" in identificador:
            usuario = User.objects.filter(
                email__iexact=identificador
            ).first()

            if usuario is not None:
                attrs["username"] = usuario.username

        return super().validate(attrs)


class RegistroSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    password2 = serializers.CharField(
        write_only=True
    )

    nombre_completo = serializers.CharField(
        write_only=True,
        max_length=200
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password2",
            "nombre_completo",
        ]

        read_only_fields = ["id"]

    def validate(self, attrs):

        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password2": "Las contraseñas no coinciden."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        nombre_completo = validated_data.pop(
            "nombre_completo"
        )

        validated_data.pop("password2")

        password = validated_data.pop("password")

        usuario = User.objects.create_user(
            password=password,
            **validated_data
        )

        Perfil.objects.create(
            usuario=usuario,
            nombre_completo=nombre_completo
        )

        return usuario


class PerfilSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="usuario.username",
        read_only=True
    )

    email = serializers.EmailField(
        source="usuario.email",
        read_only=True
    )

    class Meta:
        model = Perfil

        fields = [
            "id",
            "username",
            "email",
            "nombre_completo",
            "cargo",
            "institucion",
            "ciudad",
            "destinatario",
            "cargo_destinatario",
            "via_1",
            "cargo_via_1",
            "via_2",
            "cargo_via_2",
            "numero_instructivo",
        ]
