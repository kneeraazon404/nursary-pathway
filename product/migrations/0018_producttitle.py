# Generated by Django 3.2.6 on 2021-08-31 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_product_is_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=250)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
    ]
