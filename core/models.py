from django.db import models
from django.utils import timezone
from django.db import transaction
from core.managers import SoftDeleteManager

# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    @transaction.atomic
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    objects = SoftDeleteManager()

    @transaction.atomic
    def restore(self, *args, **kwargs):
        """
        Restore(Undelete) only soft deleted instance.
        """
        if self.is_deleted:
            self.is_deleted = False
            self.date_deleted = None
            return super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ["-id"]
