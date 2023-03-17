import itertools
from django.db import models
from django.conf import settings
from core.models import BaseModel
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from versatileimagefield.fields import VersatileImageField

# Create your models here.


def get_upload_path(instance, filename):
    name = instance.product.title
    return f"Product/{name}/{filename}"


def get_category_upload_path(instance, filename):
    name = instance.title
    return f"Category/{name}/{filename}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="product_img"
    )
    image = VersatileImageField(
        "image",
        upload_to=get_upload_path,
        blank=True,
        null=True,
    )
    featured = models.BooleanField(
        default=False,
        help_text="Featured image of product which will be shown to a buyer",
    )
    is_active = models.BooleanField(default=False)


class Category(BaseModel):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(null=False, unique=True)
    image = models.ImageField(upload_to=get_category_upload_path, blank=True, null=True)

    @property
    def get_complete_category_name(self):
        return f"{self.parent.title}/{self.title}" if self.parent else self.title

    def _generate_slug(self):
        # max_length = self._meta.get_field("slug").max_length
        value = self.title
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Category.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = "{}-{}".format(slug_original, i)

        self.slug = slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()

        super().save(*args, **kwargs)


class ProductTitle(BaseModel):
    title = models.CharField(max_length=250)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="title_category"
    )
    unit = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Standard representation of product e.g: pot, plant, kg, meter",
    )
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title


class Product(BaseModel):
    class ProductStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    title = models.ForeignKey(
        ProductTitle,
        on_delete=models.CASCADE,
        related_name="product_title",
        null=True,
        blank=True,
    )

    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(validators=[MinValueValidator(0.00)])
    description = models.TextField(
        blank=True, null=True, help_text="Short Info about Product"
    )
    auth_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Seller of this Product",
        related_name="seller",
    )
    slug = models.SlugField(null=False, unique=True)
    status = models.CharField(
        max_length=50, choices=ProductStatus.choices, default=ProductStatus.PENDING
    )
    is_approved = models.BooleanField(default=False)

    def _generate_slug(self):
        # max_length = self._meta.get_field("slug").max_length
        value = self.title.title
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Product.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = "{}-{}".format(slug_original, i)

        self.slug = slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()

        super().save(*args, **kwargs)


class ProductHistory(models.Model):
    """
    This model tracks Product model after its update.
    It keeps track of price, quantity of Product before any changes on the model

    Code for it is in ProductSerializer's update method
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_history"
    )
    title = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(help_text="Quantity of Item")
    price = models.FloatField(help_text="Price of product per item")
    description = models.TextField(
        blank=True, null=True, help_text="Short info about Product"
    )
    category = models.CharField(max_length=100, blank=True, null=True)
