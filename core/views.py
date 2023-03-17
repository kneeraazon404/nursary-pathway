from datetime import datetime
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

import jwt
import requests
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from dj_rest_auth.registration.views import SocialConnectView, SocialLoginView
from django.conf import settings
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.timezone import now
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import GenericAPIView

# Create your views here.
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from djoser.compat import get_user_email
from djoser.conf import settings as djoser_settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.utils import aware_utcnow, datetime_from_epoch

from rest_framework.request import Request
from rest_framework.response import Response

# from user.serializers import AuthUserSerializer, BuyerAuthSerializer
from user.serializers import AuthUserSerializer, TraderAuthSerializer

from utils.auth import get_pclaim
from utils.constants import UserType
from utils.logger import logger
from rest_framework import exceptions
from .serializers import (
    EmptySerializer,
    MyTokenObtainPairSerializer,
    AllAuthUserListSerializer,
)
from fcm_django.models import FCMDevice
from django_rest_resetpassword.models import ResetPasswordToken
from django_rest_resetpassword.views import (
    ResetPasswordConfirm,
    ResetPasswordRequestToken,
    ResetPasswordValidateToken,
)
from django_rest_resetpassword.serializers import (
    EmailSerializer,
    PasswordTokenSerializer,
    TokenSerializer,
)
from django.db.models.expressions import F


# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name="index.html"))

# Serve robot.txt from vue
robots = never_cache(TemplateView.as_view(template_name="robots.txt"))
manifest = never_cache(TemplateView.as_view(template_name="manifest.json"))
service_worker = never_cache(
    TemplateView.as_view(
        template_name="service-worker.js", content_type="text/javascript"
    )
)


def refresh_cookie(response: Response):

    jwt_decoded = jwt.decode(response.data["refresh"], settings.SECRET_KEY, "HS256")
    expires = datetime.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
    if "exp" in jwt_decoded:
        expires = datetime.fromtimestamp(int(jwt_decoded["exp"]))

    args = ["refresh", response.data["refresh"]]
    kwargs = {"httponly": True, "expires": expires}
    response.set_cookie(*args, **kwargs)
    return response


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = f"{settings.UI_URL}facebook_auth/"
    client_class = OAuth2Client


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = f"{settings.UI_URL}link_facebook/"
    client_class = OAuth2Client


def create_fcm_device(request: Request, response: Response):
    try:
        jwt_decoded = jwt.decode(response.data["access"], settings.SECRET_KEY, "HS256")
        if "user_id" in jwt_decoded:
            try:
                user = get_user_model().objects.get(id=jwt_decoded["user_id"])
                response.data["user_detail"] = AuthUserSerializer(
                    user, context={"request": request}
                ).data
                if hasattr(user, "trader"):
                    response.data["user_detail"] = TraderAuthSerializer(
                        user, context={"request": request}
                    ).data
                if "fcm_token" in request.data:
                    obj, created = FCMDevice.objects.update_or_create(
                        user=user,
                        defaults={
                            "registration_id": request.data["fcm_token"],
                            "type": "android",
                        },
                    )
                    obj.save()
            except Exception as e:
                logger.exception(e)
    except Exception as e:
        logger.exception(e)
    return response


class MyObtainTokenPairView(TokenObtainPairView, GenericViewSet):
    """
    View for LOGIN.
    Custom MyObtainTokenPairView class that will send refresh token as an http only cookie.
    """

    serializer_class = MyTokenObtainPairSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        """
        API that will return access and refresh token. It will also return refresh token as an http only cookie.
        """

        username = request.data["username"]
        password = request.data["password"]

        if (username is None) or (password is None):
            raise exceptions.AuthenticationFailed("username and password required")

        user = get_user_model().objects.filter(username=username).first()
        if user is None:
            raise exceptions.ValidationError("user not found")
        if not user.check_password(password):
            raise exceptions.ValidationError("wrong password")

        response = super().post(request=request, *args, **kwargs)
        # Getting user detail by decoding access token
        response = create_fcm_device(request, response)
        response = refresh_cookie(response)
        return response


class MyTokenRefreshPairView(GenericViewSet, TokenRefreshView):
    """
    Custom TokenRefreshViewSet class that takes refresh token from cookies when refresh is not present in post data.
    It also returns refresh token if ROTATE_REFRESH_TOKENS is true and it gets 'refresh' in response's data.
    """

    # permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @extend_schema(
        responses=inline_serializer(
            name="TokenRefreshResponseSerializer",
            fields={
                "access": serializers.CharField(),
                "user_detail": AuthUserSerializer(),
            },
        )
    )
    def create(self, request, *args, **kwargs):
        """
        API that refreshes access token. This API will try to take refresh token from cookies when refresh is not present in post data.
        """
        key_name = "pclaim"
        if not "refresh" in request.data.keys():
            if "refresh" in request.COOKIES.keys():
                request.data["refresh"] = request.COOKIES["refresh"]
            else:
                response = Response(
                    {"message": "NoError", "error": "No Refresh Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
                response.delete_cookie("refresh")
                return response
        response = super().post(request=request, *args, **kwargs)

        try:
            # Getting user detail by decoding access token
            jwt_decoded = jwt.decode(
                response.data["access"], settings.SECRET_KEY, "HS256"
            )
            if "user_id" in jwt_decoded:
                try:
                    user = get_user_model().objects.get(id=jwt_decoded["user_id"])
                    response.data["user_detail"] = AuthUserSerializer(
                        user, context={"request": request}
                    ).data
                    # if hasattr(user, "buyer"):
                    #     if getattr(user.profile, "user_type") == UserType.BUYER:
                    #         response.data["user_detail"] = BuyerAuthSerializer(
                    #             user, context={"request": request}
                    #         ).data
                    if hasattr(user, "trader"):
                        # if getattr(user.profile, "user_type") == UserType.BUYER:
                        response.data["user_detail"] = TraderAuthSerializer(
                            user, context={"request": request}
                        ).data
                except Exception as e:
                    logger.exception(e)
                if key_name in jwt_decoded:
                    pclaim = get_pclaim(user)
                    if jwt_decoded[key_name] != pclaim:
                        raise InvalidToken
            # Adding refresh token if it exists in data
            if "refresh" in response.data.keys():
                response = refresh_cookie(response)
                # Uncomment the line below if you don't want to send refresh token as response data
                # response.data.pop('refresh')
        except Exception as e:
            if isinstance(e, InvalidToken):
                raise e
            logger.exception(e)
            response = Response(
                {"message": str(e)}, status=status.HTTP_401_UNAUTHORIZED
            )
            response.delete_cookie("refresh")

        return response


def blacklist_refresh_token(user):
    for token in OutstandingToken.objects.filter(user=user).exclude(
        id__in=BlacklistedToken.objects.filter(token__user=user).values_list(
            "token_id", flat=True
        )
    ):
        BlacklistedToken.objects.create(token=token)


class TokenClearView(GenericViewSet):
    """
    Create ViewSet to clear refresh token in client.
    """

    serializer_class = EmptySerializer

    def create(self, request, *args, **kwargs):
        """
        API that will clear the http only refresh token for client.
        """
        OutstandingToken.objects.filter(expires_at__lte=aware_utcnow()).delete()
        if "refresh" in request.COOKIES:
            refresh = request.COOKIES["refresh"]
            try:
                jwt_decode = jwt.decode(refresh, settings.SECRET_KEY, "HS256")
                if (
                    "jti" in jwt_decode
                    and "exp" in jwt_decode
                    and "user_id" in jwt_decode
                ):
                    jti = jwt_decode["jti"]
                    exp = jwt_decode["exp"]
                    user_id = jwt_decode["user_id"]
                    token = OutstandingToken.objects.filter(
                        jti=jti,
                        user_id=user_id,
                        expires_at=datetime_from_epoch(exp),
                    )
                    token.delete()
            except:
                pass
        response = Response()
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


class AuthView(ModelViewSet):
    serializer_class = AuthUserSerializer
    queryset = get_user_model().objects.all()
    token_generator = default_token_generator

    def get_serializer_class(self):
        if self.action == "set_password":
            if djoser_settings.SET_PASSWORD_RETYPE:
                return djoser_settings.SERIALIZERS.set_password_retype
            return djoser_settings.SERIALIZERS.set_password
        elif self.action == "reset_password":
            return djoser_settings.SERIALIZERS.password_reset
        elif self.action == "reset_password_confirm":
            if djoser_settings.PASSWORD_RESET_CONFIRM_RETYPE:
                return djoser_settings.SERIALIZERS.password_reset_confirm_retype
            return djoser_settings.SERIALIZERS.password_reset_confirm
        elif self.action == "facebook":
            return SocialLoginSerializer
        elif self.action == "connect_facebook":
            return SocialLoginSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "set_password":
            self.permission_classes = djoser_settings.PERMISSIONS.set_password
        elif self.action == "reset_password":
            self.permission_classes = djoser_settings.PERMISSIONS.password_reset
        elif self.action == "reset_password_confirm":
            self.permission_classes = djoser_settings.PERMISSIONS.password_reset_confirm
        return super().get_permissions()

    @action(["POST"], detail=False)
    def set_password(self, request, *args, **kwargs):
        """
        Method for changing password
        """

        ## TODO: Email on password change
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        response = Response(
            "Your password was changed successfully. Please Login to continue",
            status=status.HTTP_200_OK,
        )

        if djoser_settings.LOGOUT_ON_PASSWORD_CHANGE:
            response.delete_cookie("refresh")
            blacklist_refresh_token(request.user)
        elif djoser_settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return response

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = {"user": user}
            to = [get_user_email(user)]
            djoser_settings.EMAIL.password_reset(self.request, context).send(to)
        else:
            return Response(
                {
                    "message": f'Could not find any user with email "{serializer.data["email"]}"'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            djoser_settings.EMAIL.password_changed_confirmation(
                self.request, context
            ).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=EmailSerializer)
    @action(["post"], detail=False)
    def mobile_reset_password(self, request, *args, **kwargs):
        response = ResetPasswordRequestToken().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data = "A reset token has been sent to your email."
        elif response.status_code == 404:
            if "status" in response.data:
                status = response.data["status"]
                if status == "notfound":
                    response.data["message"] = "Invalid token."
                if status == "expired":
                    response.data["message"] = "Token has expired."
        return response

    @extend_schema(request=TokenSerializer)
    @action(["post"], detail=False)
    def mobile_validate_token(self, request, *args, **kwargs):
        response = ResetPasswordValidateToken().post(request, *args, **kwargs)
        if response.status_code == 404:
            if "status" in response.data:
                status = response.data["status"]
                if status == "notfound":
                    response.data["message"] = "Invalid token."
                if status == "expired":
                    response.data["message"] = "Token has expired."
        return response

    @extend_schema(request=PasswordTokenSerializer)
    @action(["post"], detail=False)
    def mobile_reset_password_confirm(self, request, *args, **kwargs):
        if "token" in request.data:
            token = request.data["token"]
            reset_password_token = ResetPasswordToken.objects.filter(key=token).first()
            user = reset_password_token.user
        response = ResetPasswordConfirm().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data = "Password Reset completed. Please login to continue!"
            if djoser_settings.LOGOUT_ON_PASSWORD_CHANGE:
                if user:
                    blacklist_refresh_token(user)
        elif response.status_code == 404:
            if "status" in response.data:
                status = response.data["status"]
                if status == "notfound":
                    response.data["message"] = "Invalid token."
                if status == "expired":
                    response.data["message"] = "Token has expired."
        return response

    @action(["post"], detail=False)
    def facebook(self, request, *args, **kwargs):
        return FacebookLogin(format_kwarg=None).post(request, *args, **kwargs)

    @action(["post"], detail=False)
    def connect_facebook(self, request, *args, **kwargs):
        return FacebookConnect(format_kwarg=None).post(request, *args, **kwargs)

    @action(detail=False)
    def get_all_user_list(self, request, *args, **kwargs):
        """
        API for listing all user's 'id' and 'username' except SuperUser(i.e Admin)
        """
        _queryset = (
            get_user_model()
            .objects.filter(is_active=True, is_superuser=False)
            .annotate(
                company_name=F("trader__company_name"),
            )
        )

        return Response(AllAuthUserListSerializer(_queryset, many=True).data)
