from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from utils.filters import PriceRangeFilter

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
import django_filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from utils.constants import UserType
from utils.logger import logger
from utils.pagination import CustomPageNumberPagination
import requests

# from utils.permissions import IsUserType
from utils.serializers import EmptySerializer, TotalSerializer
from rolepermissions.roles import get_user_roles
from user.tasks import send_user_activation
from config import settings
from rest_framework_api_key.permissions import HasAPIKey

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    AuthUserSerializer,
    TraderAuthSerializer,
    UsernameSerializer,
)

from django_rest_resetpassword.views import ResetPasswordValidateToken
from django_rest_resetpassword.serializers import TokenSerializer
from django_rest_resetpassword.models import ResetPasswordToken

from utils.user_activation_token import generate_token_for_user_activation
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404


def geo_user(geotoken):
    r = requests.get(
        f"{settings.GEOKRISHI_BASE}/api/user/profile",
        headers={"Authorization": geotoken},
    )
    r_data = r.json()
    r_data["c_id"] = r_data.pop("id")
    id_value = r_data["c_id"]
    r_data["geo_user_id"] = r_data.pop("c_id")
    geo = GeokrishiUsers.objects.filter(geo_user_id=id_value)
    if geo:
        print("User already exists")
    else:
        print("No user")
        serializer = GeoUserSerializer(data=r_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return


class UserActivationViewSet(ModelViewSet):
    """
    ViewSet for account activation
    """

    @extend_schema(request=TokenSerializer, responses=EmptySerializer)
    @action(["post"], detail=False)
    def validate_trader(self, request, *args, **kwargs):
        token_obj = ResetPasswordToken.objects.filter(key=request.data["token"]).first()
        response = ResetPasswordValidateToken().post(request, *args, **kwargs)
        if response.data["status"] == "OK":
            if token_obj and hasattr(token_obj, "user"):
                user = token_obj.user
                obj = get_object_or_404(get_user_model(), pk=user.id)
                if hasattr(obj, "is_active"):
                    obj.is_active = True
                    obj.save()
                response.data["message"] = "User has been activated"
        if response.status_code == 404:
            if "status" in response.data:
                status = response.data["status"]
                if status == "notfound":
                    response.data["message"] = "Invalid token."
                if status == "expired":
                    response.data["message"] = "Token has expired."
        return response


# class VendorSerializerViewSet(UserActivationViewSet):
#     """
#     ViewSet for registration(Create) as well as 'Read Update Delete' of Vendor.
#     """

#     serializer_class = RegisterVendorSerializer
#     queryset = (
#         get_user_model()
#         .objects
#         # filter(profile__user_type=UserType.VENDOR)
#         .select_related("profile", "vendor")
#         .order_by("-id")
#     )
#     pagination_class = CustomPageNumberPagination
#     filterset_fields = ["username"]

#     def get_serializer(self, *args, **kwargs):
#         if self.action == "change_status":
#             return EmptySerializer
#         return super().get_serializer(*args, **kwargs)

#     def perform_create(self, serializer):
#         return serializer.save()

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = self.perform_create(serializer)
#         user.is_active = False
#         user.save()
#         headers = self.get_success_headers(serializer.data)
#         site = get_current_site(request)

#         context = {
#             "domain": site.domain,
#             "site_name": site.name,
#             "protocol": "https" if request.is_secure() else "http",
#         }
#         send_buyer_activation.delay(user.id, context)

#         return Response(
#             {
#                 "notify_user": "An activation link has been sent to your email. Please check your email to continue!"
#             },
#             status=status.HTTP_201_CREATED,
#             headers=headers,
#         )

#     @action(detail=False)
#     def total_vendor_count(self, request, *args, **kwargs):
#         total = self.get_queryset().count()
#         data = {"total": total}
#         return Response(TotalSerializer(data).data)

#     @action(methods=["patch"], detail=True)
#     def change_status(self, request, *args, **kwargs):
#         """
#         Change 'is_active' status of vendor
#         """
#         partial = kwargs.pop("partial", False)
#         instance = self.get_object()
#         instance.is_active = not instance.is_active
#         serializer = AuthUserSerializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)


# class BuyerViewSet(UserActivationViewSet):
#     """
#     ViewSet for registration(Create) as well as 'Read Update Delete' of Buyer.
#     """

#     serializer_class = BuyerAuthSerializer
#     queryset = (
#         get_user_model()
#         .objects
#         # filter(profile__user_type=UserType.BUYER)
#         .select_related("profile", "buyer")
#         .order_by("-id")
#     )
#     pagination_class = CustomPageNumberPagination

#     def perform_create(self, serializer):
#         return serializer.save()

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = self.perform_create(serializer)
#         user.is_active = False
#         user.save()
#         headers = self.get_success_headers(serializer.data)
#         site = get_current_site(request)

#         context = {
#             "domain": site.domain,
#             "site_name": site.name,
#             "protocol": "https" if request.is_secure() else "http",
#         }
#         send_buyer_activation.delay(user.id, context)

#         return Response(
#             serializer.data, status=status.HTTP_201_CREATED, headers=headers
#         )


class TraderViewSet(UserActivationViewSet):
    class GroupNameFilter(django_filters.FilterSet):
        group_name = django_filters.CharFilter(method="group_name_filter")

        def group_name_filter(self, queryset, name, value):
            return queryset.filter(groups__name__icontains=value)

        class Meta:
            model = get_user_model()
            fields = ["group_name", "username"]

    serializer_class = TraderAuthSerializer
    queryset = (
        get_user_model()
        .objects.filter(groups__name__in=["vendor", "buyer"])
        .order_by("-id")
        .distinct("id")
    )
    pagination_class = CustomPageNumberPagination
    filterset_class = GroupNameFilter

    def get_serializer_class(self):
        if self.action == "send_token_through_mail":
            return UsernameSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        """
        API for registration of User(Buyer/Vendor).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        user.is_active = False
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(methods=["post"], detail=False)
    def send_token_through_mail(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        user = get_user_model().objects.filter(username=username).first()
        if user:
            site = get_current_site(request)

            ### Generate token ###
            token = generate_token_for_user_activation(request, user)
            context = {
                "token": token,
                "domain": site.domain,
                "site_name": site.name,
                "protocol": "https" if request.is_secure() else "http",
            }

            send_user_activation.delay(user.id, context)
            return Response({"status": "OK"})
        else:
            return Response(
                {"status": "No such user found"}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(responses=TotalSerializer)
    @action(detail=False)
    def total_vendor_count(self, request, *args, **kwargs):
        """
        Total count of vendor
        """
        total = (
            get_user_model().objects.filter(groups__name__in=["vendor"]).order_by("-id")
        ).count()
        data = {"total": total}
        return Response(TotalSerializer(data).data)

    @action(methods=["patch"], detail=True)
    def change_active_status_of_vendor(self, request, *args, **kwargs):
        """
        Change 'is_active' status of vendor
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        _roles = [role.get_name() for role in get_user_roles(instance)]
        if not UserType.ADMIN in _roles:
            instance.is_active = not instance.is_active
            serializer = AuthUserSerializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response(
                {"Error": "Admin user cannot be deactivated"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# class GeoUser(GenericViewSet):
#     '''
#     Import user details from geokrishi.
#     '''
#     permission_classes = [HasAPIKey]
#     serializer_class = GeoUserSerializer
#     def create(self,request, *args, **kwargs):
#         # print(request.get_context_data(self, **kwargs))
#         geotoken=request.headers.get('GEOTOKEN')
#         print(geotoken)
#         r=requests.get("settings.GEOKRISHI_BASE/api/user/profile",
#             headers={
#                 # "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ1MDM4NzY1LCJqdGkiOiJkMTY3OWQ1MzIwZjI0ODZkYjhmMGY2NWFhNzFkZmM5NSIsInVzZXJfaWQiOjUyMX0.UY3Dng6p_84VrcEcqvr0P2BRAhSvgN8o2pyuQKxEoO0"
#                 "Authorization": geotoken
#             },
#         )
#         r_data=r.json()
#         r_data['c_id']=r_data.pop('id')
#         id_value=r_data['c_id']
#         r_data['geo_user_id']=r_data.pop('c_id')
#         geo=GeokrishiUsers.objects.filter(geo_user_id=id_value)
#         if geo:
#             print("User already exists")
#         else:
#             serializer = self.get_serializer(data=r_data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#         return Response(r.json())
#         # return Response(r.json(), status=STATUS.HTTP_201_CREATED)
#     def perform_create(self, serializer):
#         serializer.save()

# class GeoProduct(ModelViewSet):
#     permission_classes = [HasAPIKey]
#     serializer_class = GeoProductSerializer
#     pagination_class = CustomPageNumberPagination
#     filter_backends = [
#         PriceRangeFilter,
#         DjangoFilterBackend,
#         # filters.SearchFilter,
#         # filters.OrderingFilter,
#     ]
#     filterset_fields = [
#         "price",
#         # "title__category",
#         "quantity",
#     ]
#     # search_fields = ["price"]
#     # ordering_fields = ["price"]

#     def get_queryset(self):
#         request = self.request
#         if self.action=="all_product":
#             print(request.geouser)
#             geo_user=GeokrishiUsers.objects.get(geo_user_id=request.geouser)
#             if geo_user.municipality:
#                 queryset=GeokrishiProduct.objects.not_deleted().filter(geo_user__municipality=geo_user.municipality)
#             elif geo_user.district:
#                 queryset=GeokrishiProduct.objects.not_deleted().filter(geo_user__district=geo_user.district)
#             elif geo_user.state:
#                 queryset=GeokrishiProduct.objects.not_deleted().filter(geo_user__state=geo_user.state)
#             else:
#                 queryset=GeokrishiProduct.objects.not_deleted()

#         elif self.action=='my_product':
#             queryset=GeokrishiProduct.objects.not_deleted().filter(geo_user=request.geouser)
#         else:# except my products
#             queryset=GeokrishiProduct.objects.not_deleted().exclude(geo_user=request.geouser)
#         return queryset

#     @action(detail=False, methods=["get"], url_path='all_product',)
#     def all_product(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)

#     @action(detail=False, methods=["get"], url_path='my_product',)
#     def my_product(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)

#     def create(self,request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(serializer.data)
#     def perform_create(self, serializer):
#         serializer.save()

# class Acess(GenericViewSet):
#     '''
#     create user in samuhik with the given username,password and give acces to geokrishi
#     '''
#     serializer_class = UserSerializer

#     def perform_create(self, serializer):
#         return serializer.save()

#     def create(self,request, *args, **kwargs):
#         username_=request.data.get('username')
#         password_=request.data.get('password')
#         ##create user/trader with that username and password
#         if not username_:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)

#             user = self.perform_create(serializer)
#             user.is_active = False
#             user.save()

#         r = requests.post(settings.GEOKRISHI_URL,
#         # "http://localhost:8000/o/token/",
#         # "http://geokrishi.farm/o/token/",
#             data={
#                 "grant_type": "password",
#                 "username": username_,
#                 "password": password_,
#                 "client_id": "YzdwgUwzhhY3L2gj6OzIZl55epfwVlmxzqoARJEz",
#                 "client_secret": "3m8qgcHfikfS2d0WH8s7LUAVhfF4QMFL4hQN7q4wkSHJNpW6ptLGMtTJzH4md1xfEiaE30wgVJDjgrYIQiNu0AzIwvYnSueVKd6oUeHbUnjDcsqZBMpZQM6zBdHU5CNC",
#             },
#         )
#         status_code = r.status_code
#         print(status_code)
#         if not status_code == 200:
#             raise Exception("Error accessing to samuhik, please try again")
#         response = r.text
#         response_json = r.json()
#         return Response(response_json)
