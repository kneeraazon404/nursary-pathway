# Generated by Django 3.2.10 on 2021-12-20 10:18

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('notice', models.TextField()),
                ('type', models.CharField(choices=[('Group', 'Group'), ('Single', 'Single'), ('All', 'All')], max_length=10)),
                ('group_user_send', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50, null=True), blank=True, default=list, size=None)),
                ('redirect_data', models.JSONField(blank=True, null=True)),
                ('is_visited', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('single_user_send', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
    ]
