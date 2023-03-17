# Generated by Django 3.2.13 on 2022-07-05 06:52

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geouser', '0014_auto_20220614_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='geokrishiusers',
            name='project',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, help_text='Association with partner projects', size=None),
        ),
    ]
