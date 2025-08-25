import uuid
from django.db import models
from .telegram_user_models import TelegramUserModel


class TelegramCommandModel(models.Model):
    """
    Logs actions/commands performed by Telegram users.
    """

    class CommandType(models.TextChoices):
        START = "start", "Start"
        HELP = "help", "Help"
        USAGE = "usage", "Usage"
        REQUEST = "request", "Request"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    telegram_user = models.ForeignKey(
        TelegramUserModel,
        on_delete=models.CASCADE,
        related_name="commands",
        help_text="The Telegram user who performed this action",
    )

    command_type = models.CharField(
        max_length=50,
        choices=CommandType.choices,
        default=CommandType.START,
        help_text="Type of command/action performed",
    )

    message = models.TextField(
        blank=True,
        null=True,
        help_text="Raw message or description of the action",
    )

    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    metadata: models.JSONField = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional JSON data for extra info, e.g., parameters or context",
    )

    class Meta:
        indexes = [
            models.Index(fields=["telegram_user"]),
            models.Index(fields=["command_type"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]
        verbose_name = "Telegram Command"
        verbose_name_plural = "Telegram Commands"

    def __str__(self) -> str:
        return f"{self.telegram_user} -> {self.command_type} at {self.created_at:%Y-%m-%d %H:%M:%S}"

    # ---------- Utility Methods ----------

    @classmethod
    def log(
        cls,
        telegram_user: TelegramUserModel,
        command_type: str,
        message: str = "",
        **metadata,
    ):
        """
        Convenient method to create a log entry.
        Example: TelegramCommand.log(user, TelegramCommand.CommandType.REQUEST, "Checked crypto price")
        """
        return cls.objects.create(
            telegram_user=telegram_user,
            command_type=command_type,
            message=message,
            metadata=metadata or None,
        )
