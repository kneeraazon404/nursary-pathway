from django.apps import apps
from django.contrib import admin
from .models import Order, Quotation
from django.contrib.admin.sites import AlreadyRegistered


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "buyer",
        "product_title",
        "quantity",
        "description",
        "offer",
        "status",
    ]


admin.site.register(Order, OrderAdmin)

buyer_app_models = apps.get_app_config("buyer_app").get_models()
for model in buyer_app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
