
from django.urls import reverse
from rest_framework import serializers

from .models import Actividad


class ActividadSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    def get_imagen(self, obj):
        if not obj.imagen:
            return None

        request = self.context.get("request")
        path = reverse("actividad-imagen", kwargs={"pk": obj.pk})

        if request is None:
            return path

        return request.build_absolute_uri(path)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["imagen"] = self.get_imagen(instance)
        return data

    class Meta:
        model = Actividad
        fields = [
            "id",
            "fecha",
            "descripcion",
            "imagen",
            "creado_en",
            "actualizado_en",
        ]

        read_only_fields = [
            "id",
            "creado_en",
            "actualizado_en",
        ]

    def validate_descripcion(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "La actividad no puede estar vacía."
            )

        return value

    def update(self, instance, validated_data):
        if "imagen" in validated_data and validated_data["imagen"] is None:
            instance.imagen.delete(save=False)
            instance.imagen = None

        return super().update(instance, validated_data)
