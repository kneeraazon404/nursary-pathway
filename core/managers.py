from django.db import transaction
from django.contrib.gis.db import models


class SoftDeleteQuerySet(models.QuerySet):
    def soft_delete(self):
        for model_instance in self.all():
            if not model_instance.is_deleted:
                model_instance.soft_delete()

    def only_deleted(self):
        return self.filter(is_deleted=True)

    def not_deleted(self):
        return self.filter(is_deleted=False)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def all_deleted(self):
        return self.get_queryset().only_deleted()

    def not_deleted(self):
        return self.get_queryset().not_deleted()
