# Generated by Django 3.2.13 on 2022-07-11 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geouser', '0020_alter_geokrishiproduct_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geokrishiproduct',
            name='status',
            field=models.CharField(choices=[['available', 'available'], ['sold', 'sold']], default='available', max_length=50),
        ),
    ]
