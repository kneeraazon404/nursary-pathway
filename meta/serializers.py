from rest_framework.serializers import ModelSerializer

from .models import District, Palika, Province


class ProvinceSerializer(ModelSerializer):
    class Meta:
        model = Province
        fields = [
            "id",
            "name",
        ]


class DistrictSerializer(ModelSerializer):
    class Meta:
        model = District
        fields = [
            "id",
            "name",
            "province",
        ]


class PalikaSerializer(ModelSerializer):
    class Meta:
        model = Palika
        fields = [
            "id",
            "name",
            "district",
        ]
