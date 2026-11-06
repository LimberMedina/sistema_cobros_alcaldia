
from rest_framework import serializers
from .models import Actividad


class ActividadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actividad
        fields = [
            "id",
            "fecha",
            "descripcion",
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
