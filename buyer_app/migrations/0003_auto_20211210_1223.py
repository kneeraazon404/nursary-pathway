# Generated by Django 3.2.10 on 2021-12-10 06:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('buyer_app', '0002_auto_20210927_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='buyer',
            field=models.ForeignKey(limit_choices_to=models.Q(('groups__name', 'buyer')), on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='quotation',
            name='buyer',
            field=models.ForeignKey(limit_choices_to=models.Q(('groups__name', 'buyer')), on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
