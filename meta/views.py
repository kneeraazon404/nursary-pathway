from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend

from meta.models import District, Palika, Province
from meta.serializers import DistrictSerializer, PalikaSerializer, ProvinceSerializer


class ProvinceViewSet(GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProvinceSerializer
    queryset = Province.objects.all()


class DistrictViewSet(GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = DistrictSerializer
    queryset = District.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["province"]


class PalikaViewSet(GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PalikaSerializer
    queryset = Palika.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["district"]
