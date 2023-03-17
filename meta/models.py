from django.db import models


class Province(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"


class District(models.Model):
    name = models.CharField(max_length=250)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"


class Palika(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"
