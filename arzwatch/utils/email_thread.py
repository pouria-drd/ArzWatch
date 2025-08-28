import threading
from logging import getLogger
from django.core.mail import send_mail

# Initialize logger for email notifications
logger = getLogger("email_thread")


class EmailThread(threading.Thread):
    """Thread for sending emails asynchronously."""

    def __init__(
        self,
        subject: str,
        message: str,
        from_email: str,
        recipient_list: list,
        fail_silently=False,
        is_admin_alert=False,
    ):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.fail_silently = fail_silently
        self.is_admin_alert = is_admin_alert
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                subject=self.subject,
                message=self.message,
                from_email=self.from_email,
                recipient_list=self.recipient_list,
                fail_silently=self.fail_silently,
            )
            if self.is_admin_alert:
                logger.info(
                    f"Sent admin alert email to {self.recipient_list} with subject {self.subject}"
                )
            else:
                logger.info(
                    f"Sent email to {self.recipient_list} with subject {self.subject}"
                )

        except Exception as e:
            logger.error(f"Failed to send email to {self.recipient_list}: {str(e)}")
