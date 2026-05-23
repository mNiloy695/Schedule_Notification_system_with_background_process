import logging
from celery import shared_task
from django.utils import timezone
from .models import Notification

logger = logging.getLogger(__name__)
@shared_task(bind=True, max_retries=3)
def send_notification_task(self, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found.")
        return

    if notification.status in ["sent", "failed"]:
        logger.warning(
            f"Notification {notification_id} already {notification.status}"
        )
        return

    try:
        logger.info(
            f"Sending notification {notification_id} "
            f"to {notification.created_by.email}"
        )

       

        notification.status = "sent"
        notification.save(update_fields=["status"])

        logger.info(f"Notification {notification_id} sent successfully.")

    except Exception as exc:

        current_retry = self.request.retries + 1

        notification.retry_count = current_retry

        if current_retry >= self.max_retries:
            notification.status = "failed"
            notification.save(update_fields=["retry_count", "status"])

            logger.error(
                f"Notification {notification_id} failed permanently."
            )
            return

        notification.save(update_fields=["retry_count"])

        countdown_delay = 15 * current_retry

        logger.warning(
            f"Retrying notification {notification_id} "
            f"in {countdown_delay} seconds."
        )

        raise self.retry(
            exc=exc,
            countdown=countdown_delay
        )
