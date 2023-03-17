# Generated by Django 3.2.10 on 2021-12-13 08:45

from django.db import migrations, models
import django.db.models.deletion
import product.models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0028_product_unit"),
        ("user", "0009_auto_20211210_1224"),
    ]

    operations = [
        migrations.AddField(
            model_name="trader",
            name="category_associated_with",
            field=models.ManyToManyField(
                limit_choices_to=models.Q(("parent", None)),
                related_name="categories_of",
                to="product.Category",
            ),
        ),
    ]