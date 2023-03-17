from django.contrib import admin
from .models import Product, ProductImage, ProductHistory, Category, ProductTitle
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    search_fields = ["title__title", "created_at", "updated_at"]
    list_display = [
        "title",
        "quantity",
        "price",
        "auth_user",
        "is_approved",
        "created_at",
        "updated_at",
    ]
    list_filter = ["title", "quantity", "price", "created_at"]
    prepopulated_fields = {"slug": ("title",)}

    class Meta:
        model = Product


class ProductHistoryAdmin(admin.ModelAdmin):
    search_fields = ["product", "created_at"]
    list_display = ["product", "quantity", "price", "created_at"]
    list_filter = ["product", "quantity", "price", "created_at"]

    class Meta:
        models = ProductHistory


class CategoryAdmin(admin.ModelAdmin):
    search_fields = [
        "title",
    ]
    list_display = ["title", "slug"]
    list_filter = [
        "title",
    ]
    prepopulated_fields = {"slug": ("title",)}

    class Meta:
        model = Category


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductTitle)
admin.site.register(ProductImage)
admin.site.register(ProductHistory, ProductHistoryAdmin)
admin.site.register(Category, CategoryAdmin)

product_app_models = apps.get_app_config("product").get_models()
for product_models in product_app_models:
    try:
        admin.site.register(product_models)
    except AlreadyRegistered:
        pass
