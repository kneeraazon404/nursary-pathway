from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

meta_models = apps.get_app_config("meta").get_models()
for model in meta_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
