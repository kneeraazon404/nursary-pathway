# Generated by Django 3.2.13 on 2022-07-05 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geouser', '0017_merge_20220705_1443'),
    ]

    operations = [
        migrations.RenameField(
            model_name='geokrishisubcategory',
            old_name='name_ne',
            new_name='name_nep',
        ),
    ]