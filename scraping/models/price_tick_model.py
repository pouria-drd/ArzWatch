import uuid
from django.db import models
from django.core.exceptions import ValidationError

from .source_model import SourceModel
from .instrument_model import InstrumentModel


class PriceTickModel(models.Model):
    class Currency(models.TextChoices):
        EUR = "EUR", "Euro"
        USD = "USD", "US Dollar"
        USDT = "USDT", "Tether"
        IRR = "IRR", "Iranian Rial"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source = models.ForeignKey(
        SourceModel, on_delete=models.CASCADE, related_name="price_ticks"
    )

    instrument = models.ForeignKey(
        InstrumentModel, on_delete=models.CASCADE, related_name="price_ticks"
    )

    price = models.DecimalField(max_digits=20, decimal_places=2)

    currency = models.CharField(
        max_length=5, choices=Currency.choices, default=Currency.IRR, db_index=True
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    meta = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.instrument.symbol} price from {self.source.name}"

    def clean(self):
        # Validate price is non-negative
        if self.price < 0:
            raise ValidationError({"price": "Price must be non-negative."})

    class Meta:
        # Unique constraint to prevent duplicate price ticks for the same instrument, source, and timestamp
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "source", "timestamp"],
                name="unique_instrument_source_timestamp",
            )
        ]
        indexes = [
            models.Index(fields=["instrument", "timestamp"]),
            models.Index(fields=["source", "timestamp"]),
        ]
        ordering = ["-timestamp"]
        verbose_name = "Price Tick"
        verbose_name_plural = "Price Ticks"
