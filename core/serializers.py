from dj_rest_auth.serializers import JWTSerializer
from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user.serializers import AuthUserSerializer


class JWTCustomSerializer(JWTSerializer):
    """
    Serializer for JWT authentication.
    """

    access = serializers.CharField(source="access_token")
    refresh = serializers.CharField(source="refresh_token")
    user_detail = serializers.SerializerMethodField(method_name="get_user")


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer for LOGIN.
    """

    fcm_token = serializers.CharField(max_length=250, required=False)

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token["username"] = user.username
        return token


class EmptySerializer(Serializer):
    """
    Empty Seralizer that does not take or return any value
    """

    pass


class AllAuthUserListSerializer(AuthUserSerializer):
    """
    Serializer that returns id and username of all users except superuser
    """

    company_name = serializers.CharField()

    class Meta(AuthUserSerializer.Meta):
        fields = ["id", "username", "company_name"]
