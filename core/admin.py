from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rolepermissions.roles import get_user_roles
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

# Register your models here.


class UserAdmin(BaseUserAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
        "groups_name",
    ]

    @admin.display(empty_value="unknown")
    def groups_name(self, obj):
        return [role.get_name() for role in get_user_roles(obj)]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

meta_models = apps.get_app_config("core").get_models()

for model in meta_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
