# Generated by Django 3.2.10 on 2021-12-14 04:13

from django.db import migrations
import product.models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0028_product_unit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=versatileimagefield.fields.VersatileImageField(
                blank=True,
                null=True,
                upload_to=product.models.get_upload_path,
                verbose_name="image",
            ),
        ),
    ]
