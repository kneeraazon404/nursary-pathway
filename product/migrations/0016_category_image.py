# Generated by Django 3.2.5 on 2021-08-12 07:11

from django.db import migrations, models
import product.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_auto_20210811_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=product.models.get_category_upload_path),
        ),
    ]