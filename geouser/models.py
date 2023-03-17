from datetime import datetime

from core.managers import SoftDeleteManager
from core.models import BaseModel
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils.text import slugify
from meta.models import District, Palika, Province
from mptt.models import MPTTModel, TreeForeignKey
from utils.constants import UserType
from utils.validations import mobile_number_validation, phone_number_validation


def get_geoupload_path(instance, filename):
    name = instance.product.title
    return f"GeoProduct/{name}/{filename}"


def get_geocategory_upload_path(instance, filename):
    name = instance.title
    return f"GeoCategory/{name}/{filename}"


# class GeokrishiCategory(MPTTModel):
#     parent = TreeForeignKey(
#         "self",
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         related_name="children",
#     )
#     title = models.CharField(max_length=100)
#     slug = models.SlugField(null=False, unique=True)
#     image = models.ImageField(upload_to=get_geocategory_upload_path, blank=True, null=True)

#     # class MPTTMeta:
#     #     order_insertion_by=['']

#     @property
#     def get_complete_category_name(self):
#         return f"{self.parent.title}/{self.title}" if self.parent else self.title

#     def __str__(self):
#         return f"{self.title}"


class GeokrishiCategory(models.Model):
    name = models.CharField(max_length=255)
    name_ne = models.CharField(max_length=255, null=True)

    objects = SoftDeleteManager()

    def __str__(self):
        return f"{self.name}"


class GeokrishiSubCategory(models.Model):
    name = models.CharField(max_length=255)
    name_nep = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(GeokrishiCategory, on_delete=models.CASCADE)

    objects = SoftDeleteManager()

    def __str__(self):
        return f"{self.name}"


class Acess(models.Model):
    name = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.name}"


class GeokrishiUsers(BaseModel):
    """
    Store information of Geokrishi users.
    """

    geo_user_id = models.IntegerField(primary_key=True)

    # user = models.OneToOneFigeo_user_ideld(
    #     User, on_delete=models.CASCADE, null=True, blank=True, related_name="geokrishi"
    # )
    project = ArrayField(
        base_field=models.IntegerField(),
        default=list,
        help_text="Association with partner projects",
    )
    firstName = models.CharField(max_length=50, null=True, blank=True)
    lastName = models.CharField(max_length=50, null=True, blank=True)
    # photo = models.ImageField(
    #     null=True,
    #     blank=True,
    #     upload_to="media/images/user/photo/",
    #     help_text="User Photo, Maximum file size allowed is 2Mb",
    # )
    photo = models.CharField(max_length=500, null=True, blank=True)

    voter_card = models.ImageField(
        null=True,
        blank=True,
        upload_to="media/images/user/voter/",
        help_text="Voter Card or Citizenship, Maximum file size allowed is 2Mb",
    )
    device_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        unique=True,
        # error_messages={"unique": constants.ALREADY_REGISTERED_FROM_PHONE},
    )

    # Personal Information
    contactNo = models.BigIntegerField(
        null=True,
        blank=True,
        # validators=[validate_contact_number],
        help_text="Mobile Number",
    )
    mobileType = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        # choices=MOBILE_TYPE,
        help_text="Type of mobile device",
    )
    alternateNo = models.CharField(
        max_length=200, null=True, blank=True, help_text="Alternate mobile number"
    )

    sex = models.CharField(
        max_length=50,
        # choices=SEX,
        null=True,
        blank=True,
    )
    age = models.IntegerField(null=True, blank=True)
    disability = models.CharField(
        max_length=50,
        # choices=Disability,
        null=True,
        blank=True,
    )
    maritalStatus = models.CharField(
        max_length=50,
        # choices=MaritalStatus,
        null=True,
        blank=True,
    )
    education = models.CharField(
        max_length=50,
        null=True,
        # choices=Education,
        blank=True,
    )
    ethnicity = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        # choices=Ethnicity
    )
    religion = models.CharField(
        max_length=50,
        # choices=Religion,
        null=True,
        blank=True,
    )

    # verification
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, blank=True, null=True)
    phone_otp = models.CharField(max_length=6, blank=True, null=True)
    email_time = models.DateTimeField(blank=True, null=True)
    phone_time = models.DateTimeField(blank=True, null=True)

    # Location Information
    state = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, db_index=True
    )
    # districid = models.ForeignKey(District, on_delete=models.CASCADE,  null=True, db_index=True)
    # muniid = models.ForeignKey(Palika, on_delete=models.CASCADE,  null=True,db_index=True)
    district = models.CharField(max_length=150, null=True, blank=True, db_index=True)
    municipality = models.CharField(
        max_length=150, null=True, blank=True, db_index=True
    )

    wardNo = models.IntegerField(null=True, blank=True)
    tole = models.CharField(max_length=150, null=True, blank=True, db_index=True)
    settlement_name = models.CharField(max_length=50, null=True, blank=True)
    # location = models.PointField(null=True, blank=True)

    # Company Information
    company_name = models.CharField(
        max_length=255, null=True, blank=True, help_text="Agrovet Name"
    )
    # company_state = models.CharField(max_length=255, null=True, blank=True,help_text='Agrovet Name')
    company_state = models.IntegerField(null=True, blank=True)
    company_district = models.IntegerField(null=True, blank=True)
    company_municipality = models.IntegerField(null=True, blank=True)
    company_wardNo = models.IntegerField(null=True, blank=True)
    company_tole = models.CharField(
        max_length=150, null=True, blank=True, db_index=True
    )
    # company_registration = models.ImageField(null=True, blank=True, upload_to='media/images/company/registration',
    #    help_text='Company Registration, Maximum file size allowed is 2Mb')
    # company_PAN = models.ImageField(null=True, blank=True, upload_to='media/images/company/PAN/',
    #    help_text='PAN, Maximum file size allowed is 2Mb')

    family_size = models.IntegerField(null=True, blank=True)

    weather_station = models.IntegerField(null=True, blank=True)

    promo_code = models.CharField(null=True, blank=True, max_length=20)

    class Meta:
        ordering = ["geo_user_id"]

    @property
    def full_name(self):
        """
        Get full name of user.
        """
        firstName = str(self.firstName).capitalize() if self.firstName else None
        lastName = str(self.lastName).capitalize() if self.lastName else None
        return f"{firstName} {lastName}"

    def __str__(self):
        return f"{self.full_name}"

    def get_basic_info(self):
        return {"geo_user_id": self.geo_user_id, "name": self.full_name}

    def generate_otp(self, type="phone"):
        if type == "email":
            if self.is_email_verified:
                return {"message": "Email Already Verified"}
            self.email_otp = random.randint(111111, 999999)
            send_otp_to_mail(self)
            self.email_time = timezone.now()
        elif type == "phone":
            if self.is_phone_verified:
                return {"message": "Phone Already Verified"}
            self.phone_otp = random.randint(111111, 999999)
            send_otp_to_sms(str(self.contactNo) + ",", self.phone_otp)
            self.phone_time = timezone.now()
        self.save()
        # return {'message':f'Account Verification OTP is sent to your {type}'}

    def verify_otp(self, otp, type="phone"):
        if type == "email":
            if self.is_email_verified:
                return {"message": "Email Already Verified", "status": True}
            time = (timezone.now() - self.email_time).seconds
            if time > settings.OTP_EXPIRY_TIME:
                return {"message": "OTP Expired", "status": False}
            if otp == self.email_otp:
                self.is_email_verified = True
                self.save()
                return {"message": "Email verified success", "status": True}
            return {"message": "Invalid OTP Code", "status": False}
        elif type == "phone":
            # return verify_otp_phone(self,otp,type='phone')
            if self.is_phone_verified:
                return {"message": "Phone Already Verified", "status": True}
            time = (timezone.now() - self.phone_time).seconds
            if time > settings.OTP_EXPIRY_TIME:
                return {"message": "OTP Expired", "status": False}
            if otp == self.phone_otp:
                self.is_phone_verified = True
                self.save()
                return {"message": "Phone Verified Success", "status": True}
            return {"message": "Invalid OTP Code", "status": False}


class GeoItems(BaseModel):
    name = models.CharField(max_length=150, null=True)
    name_nep = models.CharField(max_length=150, null=True)

    marked_price = models.FloatField(validators=[MinValueValidator(0.00)], null=True)

    description = models.TextField(
        blank=True, null=True, help_text="Short Info about Product"
    )

    unit = models.CharField(null=True, blank=True, max_length=20)

    photo = models.ImageField(
        null=True,
        blank=True,
        upload_to="media/images/geouser_products/",
        help_text="User Photo, Maximum file size allowed is 2Mb",
    )  # defaultpic required

    sub_category = models.ForeignKey(
        GeokrishiSubCategory,
        on_delete=models.CASCADE,
        related_name="geosubcategory",
        null=True,
    )

    def __str__(self):
        return f"{self.name_nep}"


class GeokrishiProduct(BaseModel):
    # name=models.CharField(max_length=150,null=True)
    choices = (["market", "market"], ["self", "self"])

    AVAILABLE = "available"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELED = "canceled"

    statuses = (
        [AVAILABLE, AVAILABLE],
        [SOLD, SOLD],
        [EXPIRED, EXPIRED],
        [CANCELED, CANCELED],
    )
    items = models.ForeignKey(
        GeoItems,
        on_delete=models.CASCADE,
        related_name="items",
        default=1,
    )
    geo_user = models.ForeignKey(
        GeokrishiUsers,
        on_delete=models.CASCADE,
        help_text="Seller of this Product",
        related_name="sellers",
    )
    quantity = models.PositiveIntegerField(default=1)

    # selling_type=models.CharField(
    #     max_length=50, choices=choices, default="market"
    # )
    # unit=models.CharField(
    #     max_length=50, null=True,blank=True
    # )
    status = models.CharField(
        max_length=50,
        choices=statuses,
        default="available",
    )  # error_messages={'required': "Choices are available, sold and expired "}

    selling_price = models.FloatField(validators=[MinValueValidator(0.00)], null=True)
    sold_date = models.DateTimeField(null=True, blank=True)

    description = models.TextField(
        blank=True, null=True, help_text="Short Info about Product"
    )
    available_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    available_date_nep = models.CharField(max_length=150, null=True, blank=True)
    expiry_date_nep = models.CharField(max_length=150, null=True, blank=True)

    available_date_eng = models.DateField(null=True, blank=True)
    expiry_date_eng = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # if self.selling_type=="market":
        #     try:
        #         item=GeoItems.objects.get(id=self.items.id)
        #         print("item",item)
        #         if item.marked_price:
        #             marked_price=item.marked_price
        #             self.selling_price=marked_price
        #     except:
        #         pass
        # if self.is_expired:
        #     self.status=GeokrishiProduct.EXPIRED
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.items}"

    @property
    def is_expired(self):
        """
        expired items
        """
        if datetime.now() > self.available_date_eng:
            return True
        return False

    # photo=models.ImageField(null=True,
    #     blank=True,
    #     upload_to="media/images/geouser_products/",
    #     help_text="User Photo, Maximum file size allowed is 2Mb",
    # )#defaultpic required

    # category = models.ForeignKey(
    #     GeokrishiCategory,
    #     on_delete=models.CASCADE,
    #     related_name="geokrishicategory",
    #     null=True
    # )
    # sub_category = models.ForeignKey(
    #     GeokrishiSubCategory,
    #     on_delete=models.CASCADE,
    #     related_name="geokrishisubcategory",
    #     null=True
    # )

    # class Meta:
    #     unique_together = ("category","sub_category","name","geo_user")

    # auth_user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     help_text="Seller of this Product",
    #     related_name="seller",
    # )
    # slug = models.SlugField(null=False, unique=True)
    # status = models.CharField(
    #     max_length=50, choices=ProductStatus.choices, default=ProductStatus.PENDING
    # )
    # is_approved = models.BooleanField(default=False)

    # def _generate_slug(self):
    #     # max_length = self._meta.get_field("slug").max_length
    #     value = self.title.title
    #     slug_candidate = slug_original = slugify(value, allow_unicode=True)
    #     for i in itertools.count(1):
    #         if not Product.objects.filter(slug=slug_candidate).exists():
    #             break
    #         slug_candidate = "{}-{}".format(slug_original, i)

    #     self.slug = slug_candidate

    #
