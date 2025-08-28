from uuid import uuid4
from django.db import models
from .telegram_user_models import TelegramUserModel


class TelegramMessageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    content = models.TextField(verbose_name="Message Content")
    recipient = models.ForeignKey(
        TelegramUserModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Recipient (Leave blank for all)",
    )

    is_sent = models.BooleanField(default=False, verbose_name="Is Sent")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Sent At")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Telegram Message"
        verbose_name_plural = "Telegram Messages"

    def __str__(self):
        return f"Message to {self.recipient or 'All Users'}"
