# Generated by Django 3.2.10 on 2022-04-26 06:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_acess_geokrishicategory_geokrishiproduct_geokrishisubcategory_geokrishiusers'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Acess',
        ),
        migrations.DeleteModel(
            name='GeokrishiCategory',
        ),
        migrations.RemoveField(
            model_name='geokrishiproduct',
            name='geo_user',
        ),
        migrations.DeleteModel(
            name='GeokrishiSubCategory',
        ),
        migrations.RemoveField(
            model_name='geokrishiusers',
            name='district',
        ),
        migrations.RemoveField(
            model_name='geokrishiusers',
            name='municipality',
        ),
        migrations.RemoveField(
            model_name='geokrishiusers',
            name='state',
        ),
        migrations.DeleteModel(
            name='GeokrishiProduct',
        ),
        migrations.DeleteModel(
            name='GeokrishiUsers',
        ),
    ]