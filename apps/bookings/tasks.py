from celery import shared_task
from django.utils import timezone
from .notification_service import NotificationService
from .models import Notification
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_pending_notifications():
    """Celery task to send pending notifications"""
    try:
        NotificationService.send_pending_notifications()
        logger.info("Successfully processed pending notifications")
        return "Success"
    except Exception as e:
        logger.error(f"Failed to process pending notifications: {e}")
        return f"Error: {e}"


@shared_task
def schedule_daily_notifications():
    """Celery task to schedule daily notifications"""
    try:
        from .models import Booking
        from .services.models import Provider
        from datetime import date
        
        today = date.today()
        
        # Schedule notifications for today's bookings
        today_bookings = Booking.objects.filter(
            date=today,
            status__in=['pending', 'confirmed', 'active']
        )
        
        for booking in today_bookings:
            NotificationService.schedule_booking_notifications(booking)
        
        # Schedule provider notifications
        providers = Provider.objects.filter(
            user__telegram_username__isnull=False
        ).distinct()
        
        for provider in providers:
            NotificationService.schedule_today_queues_notification(provider, today)
        
        logger.info("Successfully scheduled daily notifications")
        return "Success"
    except Exception as e:
        logger.error(f"Failed to schedule daily notifications: {e}")
        return f"Error: {e}"


@shared_task
def send_booking_confirmation(booking_id):
    """Send booking confirmation notification"""
    try:
        from .models import Booking
        from .telegram_service import TelegramService
        
        booking = Booking.objects.get(id=booking_id)
        telegram_service = TelegramService()
        
        success = telegram_service.send_booking_confirmation(booking)
        
        if success:
            logger.info(f"Booking confirmation sent for booking {booking_id}")
            return "Success"
        else:
            logger.error(f"Failed to send booking confirmation for booking {booking_id}")
            return "Failed"
    except Exception as e:
        logger.error(f"Error sending booking confirmation for booking {booking_id}: {e}")
        return f"Error: {e}"


@shared_task
def send_booking_cancellation(booking_id):
    """Send booking cancellation notification"""
    try:
        from .models import Booking
        from .telegram_service import TelegramService
        
        booking = Booking.objects.get(id=booking_id)
        telegram_service = TelegramService()
        
        success = telegram_service.send_booking_cancellation(booking)
        
        if success:
            logger.info(f"Booking cancellation sent for booking {booking_id}")
            return "Success"
        else:
            logger.error(f"Failed to send booking cancellation for booking {booking_id}")
            return "Failed"
    except Exception as e:
        logger.error(f"Error sending booking cancellation for booking {booking_id}: {e}")
        return f"Error: {e}"
