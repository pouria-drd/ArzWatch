import uuid
import secrets
from django.db import models
from django.utils.timezone import now as django_now


class APIKey(models.Model):
    """
    Represents an API key for authenticating requests.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True, editable=False)

    request_count = models.PositiveIntegerField(default=0)
    max_requests = models.PositiveIntegerField(default=1000)

    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_request_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        indexes = [
            models.Index(fields=["key"]),
            models.Index(fields=["enabled"]),
        ]

    def __str__(self):
        status = "Active" if self.enabled else "Inactive"
        return f"{self.name} ({status}, {self.request_count}/{self.max_requests})"

    def is_valid(self) -> bool:
        """Return True if the API key is active, not deleted, not expired, and under usage limit."""
        if not self.enabled:
            return False

        if self.expires_at and django_now() > self.expires_at:
            self.disable()
            return False

        if self.request_count >= self.max_requests:
            return False

        return True

    def increment_usage(self) -> None:
        """Increment the request count and update last_request_at."""
        self.request_count += 1
        self.last_request_at = django_now()
        self.save(update_fields=["request_count", "last_request_at"])

    def reset_usage(self) -> None:
        """Reset request count to zero."""
        self.request_count = 0
        self.save(update_fields=["request_count"])

    def disable(self) -> None:
        """Deactivate the API key."""
        self.enabled = False
        self.save(update_fields=["enabled"])

    def regenerate_key(self) -> None:
        """Generate a new API key string."""
        self.key = self.generate_key()
        self.save(update_fields=["key"])

    @classmethod
    def generate_key(cls) -> str:
        """Generate a secure random 64-character hex API key."""
        return secrets.token_hex(32)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)
