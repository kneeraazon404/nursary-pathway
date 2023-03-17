from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered


# Register your models here.


meta_models = apps.get_app_config("notification").get_models()

for model in meta_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
