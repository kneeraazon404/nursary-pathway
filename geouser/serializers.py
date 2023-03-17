from datetime import date
from django.conf import settings

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

# from drf_writable_nested.mixins import UniqueFieldsMixin
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from utils import constants

from .models import (
    GeoItems,
    GeokrishiCategory,
    GeokrishiProduct,
    GeokrishiSubCategory,
    GeokrishiUsers,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for access model for oauth integration with django
    Depreciated
    """

    class Meta:
        model = User
        fields = [
            "username",
        ]


class GeoUserSerializer(serializers.ModelSerializer):
    """
    Geokrishi Users
    """

    # districtid=serializers.SerializerMethodField()
    # muniid=serializers.SerializerMethodField()
    class Meta:
        model = GeokrishiUsers
        fields = [
            "geo_user_id",
            "firstName",
            "lastName",
            "voter_card",
            "contactNo",
            "sex",
            "age",
            "maritalStatus",
            "education",
            "ethnicity",
            "religion",
            "state",
            "district",
            "municipality",
            "settlement_name",
            "wardNo",
            "tole",
            "project",
            "photo",
        ]

    def create(self, validated_data):

        distric = validated_data.pop("district", None)
        municipal = validated_data.pop("municipality", None)
        validated_data["district"] = distric
        validated_data["municipality"] = municipal
        super().create(validated_data)

    # def validate(self,data):
    #     data.district=int(data.district)
    #     data.municipality=int(data.municipality)


# class GeokrishiCategorySerializer(serializers.ModelSerializer):

#     parent_name = serializers.PrimaryKeyRelatedField(
#         source="parent.title", read_only=True
#     )
#     # slug = serializers.PrimaryKeyRelatedField(read_only=True)
#     category_name = serializers.SerializerMethodField(read_only=True)

#     def get_category_name(self, instance) -> str:
#         return instance.get_complete_category_name

#     def get_fields(self):
#         fields = super(GeokrishiCategorySerializer, self).get_fields()
#         fields["children"] = GeokrishiCategorySerializer(many=True, required=False)
#         return fields


#     class Meta:
#         model=GeokrishiCategory
#         fields = [
#             "id",
#             "parent",
#             "parent_name",
#             "title",
#             "slug",
#             "category_name",
#             "image",
#             ]


class GeokrishiCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GeokrishiCategory
        fields = ["id", "name"]


class GeokrishiSubCategorySerializer(WritableNestedModelSerializer):
    category_name = serializers.PrimaryKeyRelatedField(
        source="category.name", read_only=True
    )

    class Meta:
        model = GeokrishiSubCategory
        fields = ["id", "name", "category", "name_nep", "category_name"]


class GeoProductListSerializer(serializers.ModelSerializer):
    unit = serializers.PrimaryKeyRelatedField(source="items.unit", read_only=True)

    product = serializers.PrimaryKeyRelatedField(source="items.name", read_only=True)
    name_nep = serializers.PrimaryKeyRelatedField(
        source="items.name_nep", read_only=True
    )

    # image= serializers.PrimaryKeyRelatedField(source="items.photo.url", read_only=True, allow_null=True)
    image = serializers.SerializerMethodField()
    # image=serializers.ImageField(source="items.photo.url", read_only=True)
    seller = serializers.SerializerMethodField()
    phone = serializers.PrimaryKeyRelatedField(
        source="geo_user.contactNo", read_only=True
    )
    address = serializers.SerializerMethodField()
    user_photo = serializers.SerializerMethodField()

    class Meta:
        model = GeokrishiProduct
        fields = [
            "id",
            "items",
            "name_nep",
            "status",
            "image",
            "product",
            "phone",
            "address",
            "user_photo",
            "geo_user",
            "seller",
            "selling_price",
            "description",
            "quantity",
            "available_date",
            "expiry_date",
            "available_date_nep",
            "expiry_date_nep",
            "available_date_eng",
            "expiry_date_eng",
            "unit",
            "sold_date",
        ]

    def get_image(self, obj):
        if obj.items.photo:
            return f"{ self.context.get('request').build_absolute_uri('/')[:-1]}{obj.items.photo.url}"

            # return obj.items.photo.url
        return

    def get_seller(self, instance):
        name = ""
        if instance.geo_user.firstName:
            name += instance.geo_user.firstName.capitalize()
        if instance.geo_user.lastName:
            name += f" {instance.geo_user.lastName.capitalize()}"
        return name

    def get_address(self, instance):
        address = list()
        geo_user = instance.geo_user
        if geo_user.district and geo_user.district != "":
            address.append(geo_user.district)
        if geo_user.municipality and geo_user.municipality != "":
            address.append(geo_user.municipality)
        if geo_user.settlement_name and geo_user.settlement_name != "":
            address.append(geo_user.settlement_name)
        return ", ".join(address)

    def get_user_photo(self, instance):
        photo = ""
        geo_user = instance.geo_user
        if geo_user.photo and geo_user.photo != "":
            photo = f"{settings.GEOKRISHI_BASE}{geo_user.photo}"
        return photo


class GeokrishiProductSummarySerializer(serializers.Serializer):
    item_unit = serializers.CharField()

    item_name = serializers.CharField()
    total_quantity = serializers.IntegerField()

    class Meta:
        model = GeokrishiProduct
        fields = ["item_unit", "item_name", "total_quantity"]


class GeoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoItems
        fields = [
            "id",
            "name",
            "name_nep",
            "marked_price",
            "description",
            "photo",
            "sub_category",
            "unit",
        ]


class GeoProductSerializer(serializers.ModelSerializer):
    # cat=serializers.ListField(child=serializers.IntegerField())
    unit = serializers.PrimaryKeyRelatedField(source="items.unit", read_only=True)
    # AvailableDateEng=serializers.PrimaryKeyRelatedField(source="available_date_eng",read_only=True)

    class Meta:
        model = GeokrishiProduct
        fields = [
            "id",
            "items",
            "status",
            "selling_price",
            "description",
            "quantity",
            "available_date",
            "expiry_date",
            "available_date_nep",
            "expiry_date_nep",
            "available_date_eng",
            "expiry_date_eng",
            "sold_date",
            "unit",
        ]
        read_only_fields = [
            "sold_date",
        ]

    # def validate_available_date_eng(self, value):
    #     """
    #       Could not use this as response will be "available_date_eng - constants.AVAILABLE_DATE_FROM_TODAY"
    #     """
    #     if not self.instance and value < date.today():
    #         raise serializers.ValidationError(constants.AVAILABLE_DATE_FROM_TODAY)
    #     return value

    def validate(self, data):
        data = super().validate(data)
        if "available_date_eng" in data:
            available_date_eng = data["available_date_eng"]
            if not available_date_eng:
                raise serializers.ValidationError(constants.ENGLISH_DATE_REQUIRED)

            status = data.get("status")

            if self.instance:
                if self.instance.status == GeokrishiProduct.EXPIRED:
                    if (status and not status == GeokrishiProduct.SOLD) or (not status):
                        if available_date_eng < date.today():
                            raise serializers.ValidationError(
                                constants.AVAILABLE_DATE_FROM_TODAY
                            )
                    if not self.instance.available_date_eng == available_date_eng:
                        self.instance.status = GeokrishiProduct.AVAILABLE
            else:
                if available_date_eng < date.today():
                    raise serializers.ValidationError(
                        constants.AVAILABLE_DATE_FROM_TODAY
                    )
        return data


class GeoProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeokrishiProduct
        fields = [
            "id",
            "items",
            "status",
            "selling_price",
            "description",
            "quantity",
            "available_date",
            "expiry_date",
            "available_date_nep",
            "expiry_date_nep",
            "available_date_eng",
            "expiry_date_eng",
        ]

        # fields = ["status",]
