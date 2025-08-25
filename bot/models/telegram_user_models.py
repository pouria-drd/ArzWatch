import uuid
from django.db import models
from datetime import datetime
from django.utils.timezone import now as django_now


class TelegramUserModel(models.Model):
    """
    Represents a Telegram user with tracking for requests, status, and profile info.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        BANNED = "banned", "Banned"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)

    is_bot = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    language_code = models.CharField(max_length=10, blank=True, null=True)

    requests = models.PositiveIntegerField(default=0)
    max_requests = models.PositiveIntegerField(default=100)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    last_reset_at = models.DateTimeField(default=django_now)

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["username"]),
            models.Index(fields=["status"]),
            models.Index(fields=["last_seen"]),
        ]
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    def __str__(self) -> str:
        """Return the most readable name for the user."""
        return (
            self.username
            or f"{self.first_name or ''} {self.last_name or ''}".strip()
            or str(self.user_id)
        )

    # ---------- Request Management ----------

    def reset_daily_requests(self) -> None:
        """Reset the request count if a new day has started."""
        now = django_now()
        if self.last_reset_at.date() < now.date():
            self.requests = 0
            self.last_reset_at = now
            self.save(update_fields=["requests", "last_reset_at"])

    def reset_requests(self) -> None:
        """Reset the request count unconditionally."""
        self.requests = 0
        self.last_reset_at = django_now()
        self.save(update_fields=["requests", "last_reset_at"])

    def can_make_request(self) -> bool:
        """Check if the user can make a request today."""
        self.reset_daily_requests()

        if self.status != self.Status.ACTIVE:
            return False

        return self.requests < self.max_requests

    def increment_requests(self) -> bool:
        """
        Increment the request count if allowed.
        Returns True if incremented, False if limit reached.
        """
        if not self.can_make_request():
            return False

        self.requests += 1
        self.save(update_fields=["requests"])
        return True

    # ---------- Utility ----------

    @property
    def readable_name(self) -> str:
        """Return the most readable name for the user."""
        return (
            self.username
            or f"{self.first_name or ''} {self.last_name or ''}".strip()
            or str(self.user_id)
        )
