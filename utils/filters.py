from django.contrib.postgres.fields import ArrayField
from django_filters import rest_framework as django_filters
from geouser.models import GeokrishiUsers
from rest_framework.filters import BaseFilterBackend


class PriceRangeFilter(BaseFilterBackend):
    """
    Filter that filter out products between certain price ranges
    """

    def filter_queryset(self, request, queryset, view):
        min_price = request.query_params.get("min_price", None)
        max_price = request.query_params.get("max_price", None)
        if min_price and max_price:
            queryset = queryset.filter(price__gte=min_price, price__lte=max_price)
        return queryset


class ProjectFilter(BaseFilterBackend):
    """
    Filter that filter out products according to project
    """

    def filter_queryset(self, request, queryset, view):
        project = request.query_params.get("project", None)
        if project:
            queryset = queryset.filter(geo_user__project__contains=[project])
        return queryset


class NumberArrayFilter(django_filters.BaseCSVFilter, django_filters.NumberFilter):
    pass


class GeoUserFilter(django_filters.FilterSet):
    project = NumberArrayFilter(field_name="project", lookup_expr="contains")

    class Meta:
        model = GeokrishiUsers
        fields = ["project"]
