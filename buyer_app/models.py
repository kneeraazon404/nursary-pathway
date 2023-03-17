from core.models import BaseModel
from django.conf import settings
from django.db import models
from django.db.models import Q
from product.models import Product, ProductTitle
from utils.constants import UserType


class Order(BaseModel):
    class OrderStatus(models.TextChoices):
        NEW = "new", "New"
        CANCELLED = "cancelled", "Cancelled"
        PROCESSING = "processing", "Processing"
        CONFIRMED = "confirmed", "Confirmed"
        DISPATCHED = "dispatched", "Dispatched"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to=Q(groups__name=UserType.BUYER),
        related_name="order_by",
    )
    product_title = models.ForeignKey(
        ProductTitle,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="order_of",
        help_text="Order product with selected product title",
    )
    quantity = models.IntegerField()
    description = models.TextField()
    offer = models.FloatField(null=True, blank=True)
    address = models.TextField(default="", blank=True)
    status = models.CharField(
        max_length=50, choices=OrderStatus.choices, default=OrderStatus.NEW
    )
    remarks = models.CharField(max_length=150, blank=True, null=True)


class Quotation(BaseModel):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to=Q(groups__name=UserType.BUYER),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    description = models.TextField()
    estimated_delivery_date = models.DateField()
    address = models.TextField(default="", blank=True)


class ContactUs(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    class Meta:
        verbose_name_plural = "Contact Us"
