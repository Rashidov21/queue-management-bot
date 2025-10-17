from django.utils import timezone
from datetime import timedelta, datetime
from .models import Booking, Notification
from apps.services.models import Provider
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing queue notifications"""
    
    @staticmethod
    def schedule_booking_notifications(booking):
        """Schedule all notifications for a booking"""
        if not booking or not booking.client.telegram_username:
            return
        
        booking_datetime = timezone.datetime.combine(booking.date, booking.time)
        if timezone.is_naive(booking_datetime):
            booking_datetime = timezone.make_aware(booking_datetime)
        
        # Schedule customer notifications
        NotificationService._schedule_customer_notifications(booking, booking_datetime)
        
        # Schedule provider notifications
        NotificationService._schedule_provider_notifications(booking, booking_datetime)
    
    @staticmethod
    def _schedule_customer_notifications(booking, booking_datetime):
        """Schedule customer reminder notifications"""
        notifications = [
            {
                'type': 'queue_reminder_72h',
                'title': 'Navbat eslatmasi - 72 soat',
                'message': f"Salom {booking.client.full_name}! Sizning navbatingiz {booking.date} kuni {booking.time} da. 72 soat qoldi. Xizmat ko'rsatuvchi: {booking.provider.user.full_name}",
                'scheduled_for': booking_datetime - timedelta(hours=72)
            },
            {
                'type': 'queue_reminder_36h',
                'title': 'Navbat eslatmasi - 36 soat',
                'message': f"Salom {booking.client.full_name}! Sizning navbatingiz {booking.date} kuni {booking.time} da. 36 soat qoldi. Xizmat ko'rsatuvchi: {booking.provider.user.full_name}",
                'scheduled_for': booking_datetime - timedelta(hours=36)
            },
            {
                'type': 'queue_reminder_24h',
                'title': 'Navbat eslatmasi - 24 soat',
                'message': f"Salom {booking.client.full_name}! Sizning navbatingiz {booking.date} kuni {booking.time} da. 24 soat qoldi. Xizmat ko'rsatuvchi: {booking.provider.user.full_name}",
                'scheduled_for': booking_datetime - timedelta(hours=24)
            },
            {
                'type': 'queue_reminder_3h',
                'title': 'Navbat eslatmasi - 3 soat',
                'message': f"Salom {booking.client.full_name}! Sizning navbatingiz {booking.date} kuni {booking.time} da. 3 soat qoldi. Xizmat ko'rsatuvchi: {booking.provider.user.full_name}",
                'scheduled_for': booking_datetime - timedelta(hours=3)
            },
            {
                'type': 'queue_reminder_1h',
                'title': 'Navbat eslatmasi - 1 soat',
                'message': f"Salom {booking.client.full_name}! Sizning navbatingiz {booking.date} kuni {booking.time} da. 1 soat qoldi. Xizmat ko'rsatuvchi: {booking.provider.user.full_name}",
                'scheduled_for': booking_datetime - timedelta(hours=1)
            }
        ]
        
        for notif_data in notifications:
            # Only schedule if the time hasn't passed yet
            if notif_data['scheduled_for'] > timezone.now():
                Notification.objects.create(
                    user=booking.client,
                    booking=booking,
                    type=notif_data['type'],
                    title=notif_data['title'],
                    message=notif_data['message'],
                    scheduled_for=notif_data['scheduled_for'],
                    is_sent=False
                )
    
    @staticmethod
    def _schedule_provider_notifications(booking, booking_datetime):
        """Schedule provider notifications"""
        if not booking.provider.user.telegram_username:
            return
        
        # Provider next queue notification (1 hour before)
        Notification.objects.create(
            user=booking.provider.user,
            booking=booking,
            type='provider_next_queue',
            title='Keyingi navbat eslatmasi',
            message=f"Salom {booking.provider.user.full_name}! Keyingi navbat {booking.date} kuni {booking.time} da. Mijoz: {booking.client.full_name}. 1 soat qoldi.",
            scheduled_for=booking_datetime - timedelta(hours=1),
            is_sent=False
        )
    
    @staticmethod
    def schedule_today_queues_notification(provider, date):
        """Schedule notification about today's queues for provider"""
        if not provider.user.telegram_username:
            return
        
        # Get all bookings for today
        today_bookings = Booking.objects.filter(
            provider=provider,
            date=date,
            status__in=['pending', 'confirmed', 'active']
        ).order_by('time')
        
        if not today_bookings.exists():
            return
        
        # Create message with all today's queues
        message = f"Salom {provider.user.full_name}! Bugungi navbatlar:\n\n"
        for booking in today_bookings:
            status_text = {
                'pending': 'Kutilmoqda',
                'confirmed': 'Tasdiqlangan',
                'active': 'Faol'
            }.get(booking.status, booking.status)
            
            message += f"🕐 {booking.time} - {booking.client.full_name} ({status_text})\n"
        
        # Schedule for 1 hour before first booking
        first_booking_time = today_bookings.first().time
        notification_time = timezone.datetime.combine(date, first_booking_time) - timedelta(hours=1)
        if timezone.is_naive(notification_time):
            notification_time = timezone.make_aware(notification_time)
        
        if notification_time > timezone.now():
            Notification.objects.create(
                user=provider.user,
                type='provider_today_queues',
                title='Bugungi navbatlar',
                message=message,
                scheduled_for=notification_time,
                is_sent=False
            )
    
    @staticmethod
    def send_pending_notifications():
        """Send all pending notifications that are due"""
        now = timezone.now()
        pending_notifications = Notification.objects.filter(
            is_sent=False,
            scheduled_for__lte=now
        )
        
        for notification in pending_notifications:
            try:
                NotificationService._send_notification(notification)
            except Exception as e:
                logger.error(f"Failed to send notification {notification.id}: {e}")
    
    @staticmethod
    def _send_notification(notification):
        """Send a single notification via Telegram"""
        from .telegram_service import TelegramService
        
        telegram_service = TelegramService()
        success = telegram_service.send_message(
            chat_id=notification.user.telegram_username,
            message=notification.message
        )
        
        if success:
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.sent_via = 'telegram'
            notification.save()
            logger.info(f"Notification {notification.id} sent successfully")
        else:
            logger.error(f"Failed to send notification {notification.id}")
    
    @staticmethod
    def cancel_booking_notifications(booking):
        """Cancel all scheduled notifications for a booking"""
        Notification.objects.filter(
            booking=booking,
            is_sent=False
        ).delete()
    
    @staticmethod
    def update_booking_notifications(booking):
        """Update notifications when booking is modified"""
        # Cancel existing notifications
        NotificationService.cancel_booking_notifications(booking)
        
        # Schedule new notifications
        NotificationService.schedule_booking_notifications(booking)
