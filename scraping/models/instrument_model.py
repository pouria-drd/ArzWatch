import uuid
from django.db import models
from django.core.validators import RegexValidator


class InstrumentModel(models.Model):
    class Category(models.TextChoices):
        GOLD = "gold", "Gold"
        COIN = "coin", "Coin"
        CURRENCY = "currency", "Currency"
        CRYPTO = "crypto", "Crypto"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    fa_name = models.CharField(max_length=100)

    symbol = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                r"^[A-Z0-9]{2,10}$",
                "Symbol must be uppercase alphanumeric (2-10 characters).",
            )
        ],
    )

    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.CURRENCY,
        db_index=True,
    )

    default_source = models.ForeignKey(
        "SourceModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="instruments_default",
        help_text="Default source for scraping this instrument.",
    )

    enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol}"

    class Meta:
        ordering = ["symbol"]
        verbose_name = "Instrument"
        verbose_name_plural = "Instruments"
