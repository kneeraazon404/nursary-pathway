from django.contrib import admin

# from .models import Profile, Vendor, AdminEmail
from .models import Profile, AdminEmail

from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered


# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    search_fields = [
        "auth_user",
        # "user_type"
    ]
    list_display = [
        "auth_user",
        # "user_type",
        "get_is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "auth_user__username",
        "auth_user__is_active",
        # "user_type",
    ]

    class Meta:
        model = Profile

    def get_is_active(self, instance):
        return instance.auth_user.is_active

    get_is_active.short_description = "Is Active"


# class VendorAdmin(admin.ModelAdmin):
#     search_fields = ["auth_user__username", "seller_company_name"]
#     list_display = [
#         "auth_user",
#         "seller_company_name",
#         "get_is_active",
#         "created_at",
#         "updated_at",
#     ]
#     list_filter = [
#         "auth_user__is_active",
#         "created_at",
#     ]

#     class Meta:
#         model = Vendor

#     def get_is_active(self, instance):
#         return instance.auth_user.is_active

#     get_is_active.short_description = "Is Active"


class AdminEmailAdmin(admin.ModelAdmin):
    search_fields = ["name", "email"]
    list_display = [
        "name",
        "email",
    ]

    class Meta:
        model = AdminEmail


admin.site.register(Profile, ProfileAdmin)
# admin.site.register(Vendor, VendorAdmin)
admin.site.register(AdminEmail, AdminEmailAdmin)

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

user_app_models = apps.get_app_config("user").get_models()
for user_models in user_app_models:
    try:
        admin.site.register(user_models)
    except AlreadyRegistered:
        pass
