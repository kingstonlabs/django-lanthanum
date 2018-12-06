from django.db import models
from lanthanum.fields import DynamicField

from .schema_fields import music_catalog_field


class RecordShop(models.Model):
    name = models.CharField(max_length=50, unique=True)
    catalog = DynamicField(
        schema_field=music_catalog_field,
        blank=True,
        null=True
    )
