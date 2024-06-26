# Generated by Django 3.2.6 on 2021-08-31 10:45

from django.db import migrations


def create_product_titles(apps, schema_editor):
    ProductTitle = apps.get_model("product", "ProductTitle")
    Product = apps.get_model("product", "Product")

    qs = list(Product.objects.all().values_list("title", flat=True).order_by("id"))

    ProductTitle.objects.bulk_create([ProductTitle(title=x) for x in qs])


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0018_producttitle"),
    ]

    operations = [
        migrations.RunPython(create_product_titles),
    ]
