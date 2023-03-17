# Generated by Django 3.2.5 on 2021-08-02 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_product_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='about',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='producthistory',
            old_name='about',
            new_name='description',
        ),
        migrations.AddField(
            model_name='product',
            name='unit',
            field=models.CharField(blank=True, help_text='Standard measurement units.eg: kg, meter,etc..', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='producthistory',
            name='title',
            field=models.CharField(default=1, max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='producthistory',
            name='unit',
            field=models.CharField(default=1, help_text='Standard measurement units.eg: kg, meter,etc..', max_length=20),
            preserve_default=False,
        ),
    ]