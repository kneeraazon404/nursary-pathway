# Generated by Django 3.2.10 on 2022-06-14 05:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geouser', '0012_alter_geokrishiusers_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geokrishiusers',
            name='districid',
        ),
        migrations.RemoveField(
            model_name='geokrishiusers',
            name='muniid',
        ),
    ]
