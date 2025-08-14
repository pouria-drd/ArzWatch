import uuid
from django.db import models
from .instrument_model import InstrumentModel
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class SourceModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=50, unique=True, db_index=True)
    base_url = models.URLField()

    enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validate base_url format
        validator = URLValidator()
        try:
            validator(self.base_url)
        except ValidationError as e:
            raise ValidationError({"base_url": "Invalid URL format."})

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Source"
        verbose_name_plural = "Sources"


class SourceConfigModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source = models.ForeignKey(
        SourceModel, on_delete=models.CASCADE, related_name="source_configs"
    )

    instrument = models.ForeignKey(
        InstrumentModel, on_delete=models.CASCADE, related_name="source_configs"
    )

    path = models.CharField(
        max_length=255,
        help_text="URL path for scraping (e.g., profile/price_dollar_rl)",
    )

    class Meta:
        verbose_name = "Source Config"
        verbose_name_plural = "Source Configs"

    def __str__(self):
        return f"{self.source.name} config for {self.instrument.symbol}"
