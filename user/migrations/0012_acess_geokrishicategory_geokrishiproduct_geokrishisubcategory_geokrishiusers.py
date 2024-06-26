# Generated by Django 3.2.10 on 2022-04-25 10:27

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0001_initial'),
        ('user', '0011_auto_20220216_1144'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('client_id', models.CharField(max_length=255)),
                ('client_secret', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='GeokrishiCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('name_ne', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GeokrishiSubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('name_ne', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GeokrishiUsers',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('geo_user_id', models.IntegerField(primary_key=True, serialize=False)),
                ('firstName', models.CharField(blank=True, max_length=50, null=True)),
                ('lastName', models.CharField(blank=True, max_length=50, null=True)),
                ('photo', models.ImageField(blank=True, help_text='User Photo, Maximum file size allowed is 2Mb', null=True, upload_to='media/images/user/photo/')),
                ('voter_card', models.ImageField(blank=True, help_text='Voter Card or Citizenship, Maximum file size allowed is 2Mb', null=True, upload_to='media/images/user/voter/')),
                ('device_id', models.CharField(blank=True, default=None, max_length=255, null=True, unique=True)),
                ('contactNo', models.BigIntegerField(blank=True, help_text='Mobile Number', null=True)),
                ('mobileType', models.CharField(blank=True, help_text='Type of mobile device', max_length=200, null=True)),
                ('alternateNo', models.CharField(blank=True, help_text='Alternate mobile number', max_length=200, null=True)),
                ('sex', models.CharField(blank=True, max_length=50, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('disability', models.CharField(blank=True, max_length=50, null=True)),
                ('maritalStatus', models.CharField(blank=True, max_length=50, null=True)),
                ('education', models.CharField(blank=True, max_length=50, null=True)),
                ('ethnicity', models.CharField(blank=True, max_length=50, null=True)),
                ('religion', models.CharField(blank=True, max_length=50, null=True)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('is_phone_verified', models.BooleanField(default=False)),
                ('email_otp', models.CharField(blank=True, max_length=6, null=True)),
                ('phone_otp', models.CharField(blank=True, max_length=6, null=True)),
                ('email_time', models.DateTimeField(blank=True, null=True)),
                ('phone_time', models.DateTimeField(blank=True, null=True)),
                ('wardNo', models.IntegerField(blank=True, null=True)),
                ('tole', models.CharField(blank=True, db_index=True, max_length=150, null=True)),
                ('settlement_name', models.CharField(blank=True, max_length=50, null=True)),
                ('company_name', models.CharField(blank=True, help_text='Agrovet Name', max_length=255, null=True)),
                ('company_state', models.IntegerField(blank=True, null=True)),
                ('company_district', models.IntegerField(blank=True, null=True)),
                ('company_municipality', models.IntegerField(blank=True, null=True)),
                ('company_wardNo', models.IntegerField(blank=True, null=True)),
                ('company_tole', models.CharField(blank=True, db_index=True, max_length=150, null=True)),
                ('family_size', models.IntegerField(blank=True, null=True)),
                ('weather_station', models.IntegerField(blank=True, null=True)),
                ('promo_code', models.CharField(blank=True, max_length=20, null=True)),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='meta.district')),
                ('municipality', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='meta.palika')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='meta.province')),
            ],
            options={
                'ordering': ['geo_user_id'],
            },
        ),
        migrations.CreateModel(
            name='GeokrishiProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('description', models.TextField(blank=True, help_text='Short Info about Product', null=True)),
                ('geo_user', models.ForeignKey(help_text='Seller of this Product', on_delete=django.db.models.deletion.CASCADE, related_name='sellers', to='user.geokrishiusers')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
    ]
