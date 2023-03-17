from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

# from .models import Profile, Vendor, AdminEmail
from .models import (
    Acess,
    GeoItems,
    GeokrishiCategory,
    GeokrishiProduct,
    GeokrishiSubCategory,
    GeokrishiUsers,
)

# Register your models here.


# class ProfileAdmin(admin.ModelAdmin):
#     search_fields = [
#         "auth_user",
#         # "user_type"
#     ]
#     list_display = [
#         "auth_user",
#         # "user_type",
#         "get_is_active",
#         "created_at",
#         "updated_at",
#     ]
#     list_filter = [
#         "auth_user__username",
#         "auth_user__is_active",
#         # "user_type",
#     ]

#     class Meta:
#         model = Profile


class GeokrishiUsersAdmin(admin.ModelAdmin):
    search_fields = [
        "firstName",
    ]
    list_display = ["geo_user_id", "firstName"]
    list_filter = ["firstName"]

    class Meta:
        model = GeokrishiUsers


class GeokrishiProductAdmin(admin.ModelAdmin):
    search_fields = [
        "items",
        "geo_user",
    ]
    list_display = [
        "id",
        "items",
        "geo_user",
        "quantity",
        "selling_price",
        "status",
        "available_date_eng",
    ]
    list_filter = [
        "items",
        "geo_user",
    ]

    class Meta:
        model = GeokrishiProduct


class GeoItemsAdmin(admin.ModelAdmin):
    search_fields = ["name", "sub_category"]
    list_display = ["id", "name", "sub_category", "unit"]
    list_filter = ["name", "sub_category"]

    class Meta:
        model = GeoItems


class GeokrishiCategoryAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
    ]
    list_display = [
        "id",
        "name",
    ]
    list_filter = ["name"]

    class Meta:
        model = GeokrishiCategory


class GeokrishiSubCategoryAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
    ]
    list_display = [
        "id",
        "name",
    ]
    list_filter = ["name"]

    class Meta:
        model = GeokrishiSubCategory


admin.site.register(GeokrishiUsers, GeokrishiUsersAdmin)
# admin.site.register(Vendor, VendorAdmin)
admin.site.register(GeokrishiProduct, GeokrishiProductAdmin)
admin.site.register(GeoItems, GeoItemsAdmin)

admin.site.register(GeokrishiCategory, GeokrishiCategoryAdmin)
admin.site.register(GeokrishiSubCategory, GeokrishiSubCategoryAdmin)

# class AcessAdmin(admin.ModelAdmin):
#     search_fields = ["name"]
#     list_display = [
#         "name",
#         "client_id",
#     ]
# admin.site.register(Acess, AcessAdmin)

# class GeokrishiUsersAdmin(admin.ModelAdmin):
#     search_fields = ["firstName"]
#     list_display = [
#         "firstName",
#     ]
# admin.site.register(GeokrishiUsers, GeokrishiUsersAdmin)
