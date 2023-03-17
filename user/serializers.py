from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

# from drf_writable_nested.mixins import UniqueFieldsMixin
from django.contrib.auth.password_validation import validate_password
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from utils.constants import UserType

# from .models import Buyer, Profile, Vendor, Trader

from .models import Profile, Trader

from rolepermissions.roles import assign_role, get_user_roles


class ProfileSerializer(serializers.ModelSerializer):
    province_name = serializers.PrimaryKeyRelatedField(
        source="province.name", read_only=True
    )
    district_name = serializers.PrimaryKeyRelatedField(
        source="district.name", read_only=True
    )
    palika_name = serializers.PrimaryKeyRelatedField(
        source="palika.name", read_only=True
    )

    address = serializers.SerializerMethodField()

    def get_address(self, instance):
        """
        Returns combination of province, district, palika, ward and tole
        as an address
        """
        address_string = ""
        if instance.tole:
            address_string += str(instance.tole) + ","
        if instance.ward:
            address_string += str(instance.ward) + ","
        if instance.palika:
            address_string += str(instance.palika.name) + ","
        if instance.district:
            address_string += str(instance.district.name) + ","
        if instance.province:
            address_string += str(instance.province.name) + ","
        return address_string.rstrip(",")  ##Remove trailing ', ' if any

    class Meta:
        model = Profile
        fields = [
            "id",
            "auth_user",
            "province",
            "province_name",
            "district",
            "district_name",
            "palika",
            "palika_name",
            "ward",
            "tole",
            "address",
            "latitude",
            "longitude",
            # "user_type",
        ]
        extra_kwargs = {"auth_user": {"required": False}}


class AuthUserSerializer(WritableNestedModelSerializer):
    """
    Common Serializer for Registration of User.
    This serializer is Inherited by those where registration/creation of User is needed.
    Validation of password and creation of Profile is done here.

    :param user_role: Type of role for user(e.g: buyer, vendor, admin)
    """

    profile = ProfileSerializer(required=False)

    user_roles = serializers.SerializerMethodField()

    def get_user_roles(self, instance):
        _role_list = get_user_roles(instance)
        _roles = [role.get_name() for role in _role_list]
        return _roles

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "last_login",
            "user_roles",
            "profile",
            "is_active",
        ]
        read_only_fields = ("username", "date_joined", "last_login")

    def validate(self, data):
        if not "username" in data and "email" in data:
            data["username"] = data["email"]

        if (
            "password" in data
            and "password2" in data
            and data["password"] != data["password2"]
        ):
            raise serializers.ValidationError("Passwords doesnot match")

        if "username" in data:
            user_exists = (
                get_user_model().objects.filter(username=data["username"]).exists()
            )
            if not self.instance and user_exists:
                raise serializers.ValidationError(
                    "User with same username already exists"
                )

        if "password" in data and "password2" in data:
            password = data.get("password")
            data["password"] = password

            try:
                validate_password(password)
            except serializers.ValidationError as e:
                serializer_error = serializers.as_serializer_error(e)
                raise serializers.ValidationError(
                    {"password": serializer_error["non_field_errors"]}
                )
        return data

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        password2 = validated_data.pop("password2", None)

        #######
        ## We cannot access request in serializer. So, from context acsessing request.

        # _request = self.context["request"]
        # user_role = _request.query_params.get("user_role")
        #######

        instance = super().create(validated_data)

        ######
        ## The role passed in request as query_params is used to assign role to user
        for role in ["buyer", "vendor"]:
            assign_role(instance, role)
        ######

        profile = validated_data.get("profile", None)
        if not profile and not hasattr(instance, "profile"):
            try:
                profile = Profile.objects.create(
                    auth_user=instance,
                )
            except Exception as e:
                pass

        if password:
            instance.set_password(password)
            instance.profile.save()
            instance.is_active = True
        else:
            instance.set_unusable_password()
            instance.is_active = False
        instance.save()
        return instance


# class VendorSerializer(serializers.ModelSerializer):
#     """
#     Normal Vendor Serializer
#     """

#     class Meta:
#         model = Vendor
#         fields = [
#             "id",
#             "phone_number",
#             # "location",
#             "seller_company_name",
#         ]


# class RegisterVendorSerializer(AuthUserSerializer):
#     """
#     Serializer for registration of Vendor
#     """

#     password = serializers.CharField(write_only=True)
#     password2 = serializers.CharField(write_only=True)
#     vendor = VendorSerializer()

#     class Meta(AuthUserSerializer.Meta):
#         fields = AuthUserSerializer.Meta.fields + ["password", "password2", "vendor"]

#     # def create(self, validated_data):
#     #     instance = super().create(validated_data)
#     #     # if hasattr(instance, "profile"):
#     #     #     instance.profile.user_type = UserType.VENDOR
#     #     #     instance.profile.save()
#     #     return instance


# class BuyerSerializer(serializers.ModelSerializer):
#     """
#     Buyer Serializer
#     """

#     class Meta:
#         model = Buyer
#         fields = [
#             "id",
#             "company_name",
#             "contact_number",
#             "contact_person",
#             "mobile_number",
#         ]


# class BuyerAuthSerializer(AuthUserSerializer):
#     """
#     Serializer for registration of buyer
#     """

#     password = serializers.CharField(write_only=True)
#     password2 = serializers.CharField(write_only=True)
#     buyer = BuyerSerializer()

#     class Meta(AuthUserSerializer.Meta):
#         fields = AuthUserSerializer.Meta.fields + ["password", "password2", "buyer"]

#     # def create(self, validated_data):
#     #     instance = super().create(validated_data)
#     #     # if hasattr(instance, "profile"):
#     #     #     instance.profile.user_type = UserType.BUYER
#     #     #     instance.profile.save()
#     #     return instance


class TraderSerializer(serializers.ModelSerializer):
    """
    Serializer for Trader Model
    """

    class Meta:
        model = Trader
        fields = [
            "id",
            "auth_user",
            "company_name",
            "contact_person",
            "contact_number",
            "mobile_number",
            "category_associated_with",
        ]
        extra_kwargs = {"auth_user": {"required": False}}


class TraderAuthSerializer(AuthUserSerializer):
    """
    Serializer for registration of User(Buyer/Vendor)
    """

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    trader = TraderSerializer()

    class Meta(AuthUserSerializer.Meta):
        fields = AuthUserSerializer.Meta.fields + [
            "password",
            "password2",
            "trader",
        ]


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField()


# class UserSerializer(serializers.ModelSerializer):
#     class Meta():
#         model=User
#         fields = [
#             # "password",
#             "username",
#         ]
