from django.db import models
from core.models import BaseModel
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Notice(BaseModel):
    class Type(models.TextChoices):
        GROUP = "Group", "Group"
        SINGLE = "Single", "Single"
        ALL = "All", "All"

    notice = models.TextField()
    type = models.CharField(max_length=10, choices=Type.choices)
    group_user_send = ArrayField(
        models.CharField(max_length=50, blank=True, null=True), default=list, blank=True
    )
    single_user_send = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.CASCADE, blank=True, null=True
    )
    redirect_data = models.JSONField(blank=True, null=True)
    is_visited = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
