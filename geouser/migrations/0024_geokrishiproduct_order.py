# Generated by Django 3.2.14 on 2022-08-05 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geouser', '0023_auto_20220804_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='geokrishiproduct',
            name='order',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
