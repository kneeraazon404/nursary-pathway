from rest_framework import serializers


class EmptySerializer(serializers.Serializer):
    pass


class TotalSerializer(serializers.Serializer):
    total = serializers.IntegerField(read_only=True)
