from uuid import uuid4
from django.db import models
from .telegram_user_models import TelegramUserModel


class TelegramMessageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    content = models.TextField(verbose_name="Message Content")

    # Many-to-Many allows sending to multiple users
    recipients = models.ManyToManyField(
        TelegramUserModel,
        blank=True,
        related_name="messages",
        verbose_name="Recipients (Leave empty for all)",
    )

    is_sent = models.BooleanField(default=False, verbose_name="Is Sent")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Sent At")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Telegram Message"
        verbose_name_plural = "Telegram Messages"

    def __str__(self):
        if self.recipients.exists():
            return f"Message to {self.recipients.count()} user(s)"
        return "Message to All Users"
