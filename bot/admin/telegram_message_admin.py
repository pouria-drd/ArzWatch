import asyncio
import logging

from django.conf import settings
from django.contrib import admin
from django.utils import timezone

from telegram import Bot
from telegram.error import TelegramError
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest
from bot.models import TelegramMessageModel, TelegramUserModel

logger = logging.getLogger("telegram_bot")


@admin.register(TelegramMessageModel)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = (
        "content_preview",
        "recipients_preview",
        "is_sent",
        "sent_at",
        "created_at",
    )
    list_filter = ("is_sent", "created_at")
    search_fields = ("content",)
    actions = ["send_messages"]
    filter_horizontal = ("recipients",)  # Makes multi-select box easier to use

    def content_preview(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")

    content_preview.short_description = "Message Content"

    def recipients_preview(self, obj):
        if obj.recipients.exists():
            return ", ".join([str(r) for r in obj.recipients.all()])
        return "All Users"

    recipients_preview.short_description = "Recipients"

    def send_messages(self, request, queryset):
        """
        Send selected messages via proxy if configured.
        """
        request_kwargs = {}
        if getattr(settings, "TELEGRAM_PROXY_URL", None):
            request_kwargs["proxy"] = settings.TELEGRAM_PROXY_URL
            logger.info("Using proxy for Telegram bot.")

        telegram_request = HTTPXRequest(**request_kwargs)
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, request=telegram_request)

        async def send_message_async(message, recipients):
            for recipient in recipients:
                try:
                    await bot.send_message(
                        chat_id=recipient.chat_id,
                        text=message.content,
                        parse_mode=ParseMode.HTML,
                    )
                    logger.info(f"Message sent to {recipient}: {message.content}")
                except TelegramError as e:
                    logger.error(f"Error sending message to {recipient}: {str(e)}")
                    self.message_user(
                        request,
                        f"Error sending message to {recipient}: {str(e)}",
                        level="error",
                    )

        for message in queryset.filter(is_sent=False):
            recipients = (
                list(message.recipients.all())
                if message.recipients.exists()
                else TelegramUserModel.objects.filter(
                    status=TelegramUserModel.Status.ACTIVE
                )
            )

            if not recipients:
                self.message_user(request, "No recipients found.", level="error")
                continue

            # Run async loop
            asyncio.run(send_message_async(message, recipients))

            message.is_sent = True
            message.sent_at = timezone.now()
            message.save()

            self.message_user(request, f"Message sent to {len(recipients)} users.")

    send_messages.short_description = "Send selected Telegram messages"
