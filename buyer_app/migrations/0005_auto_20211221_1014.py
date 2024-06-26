# Generated by Django 3.2.10 on 2021-12-21 04:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0030_product_status'),
        ('buyer_app', '0004_auto_20211216_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='buyer',
            field=models.ForeignKey(limit_choices_to=models.Q(('groups__name', 'buyer')), on_delete=django.db.models.deletion.CASCADE, related_name='order_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_of', to='product.product'),
        ),
    ]
