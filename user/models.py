from core.models import BaseModel
from django.conf import settings
from django.db import models
from meta.models import District, Palika, Province
from utils.constants import UserType
from utils.validations import mobile_number_validation, phone_number_validation
from product.models import Category
from django.db.models import Q
from django.contrib.gis.db.models import PointField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import transaction


class AdminEmail(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class Profile(BaseModel):
    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
    )
    palika = models.ForeignKey(
        Palika,
        on_delete=models.CASCADE,
    )
    ward = models.IntegerField(blank=True, null=True)
    tole = models.CharField(max_length=255, default="")
    latitude = models.FloatField(
        blank=True, null=True, help_text="Latitude of Trader's location"
    )
    longitude = models.FloatField(
        blank=True, null=True, help_text="Longitude of Trader's location"
    )
    # user_type = models.CharField(max_length=50, choices=UserType.choices)

    def __str__(self):
        return str(self.auth_user.username)


# class Vendor(BaseModel):
#     auth_user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor"
#     )
#     phone_number = models.CharField(
#         max_length=10, blank=True, null=True, validators=[phone_number_validation]
#     )
#     # location = models.CharField(max_length=150, blank=True, null=True)
#     seller_company_name = models.CharField(max_length=250, blank=True, null=True)

#     def __str__(self):
#         try:
#             return f"{self.seller_company_name}"
#         except:
#             return str(self.auth_user.username)


# class Buyer(BaseModel):
#     auth_user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buyer"
#     )
#     company_name = models.CharField(max_length=255, help_text="Company name")
#     contact_person = models.CharField(
#         max_length=255, help_text="Name of contact person"
#     )
#     contact_number = models.CharField(
#         max_length=10,
#         validators=[phone_number_validation],
#         help_text="Contact number of company",
#     )
#     mobile_number = models.CharField(
#         max_length=10,
#         validators=[mobile_number_validation],
#         help_text="Mobile number of company/buyer",
#     )

#     def __str__(self):
#         try:
#             return f"{self.company_name}"
#         except:
#             return str(self.auth_user.username)


class Trader(BaseModel):
    """
    Model for both Buyer and Vendor
    """

    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trader"
    )
    category_associated_with = models.ManyToManyField(
        Category, limit_choices_to=Q(parent=None), related_name="categories_of"
    )
    company_name = models.CharField(max_length=250, help_text="Company name")
    contact_person = models.CharField(
        max_length=255, help_text="Name of contact person"
    )
    contact_number = models.CharField(
        max_length=10,
        validators=[phone_number_validation],
        help_text="Contact number of company",
    )
    mobile_number = models.CharField(
        max_length=10,
        validators=[mobile_number_validation],
        help_text="Mobile number of buyer/vendor",
    )

    def __str__(self):
        return str(self.auth_user.username)
