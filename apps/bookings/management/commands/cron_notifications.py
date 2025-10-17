from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bookings.notification_service import NotificationService
from apps.bookings.models import Booking, Notification
from apps.services.models import Provider
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cron job to send notifications - run every 5 minutes'
    
    def handle(self, *args, **options):
        try:
            # Send pending notifications
            self.send_pending_notifications()
            
            # Schedule notifications for upcoming bookings
            self.schedule_upcoming_notifications()
            
            self.stdout.write(self.style.SUCCESS('Notification cron job completed successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Notification cron job failed: {e}'))
            logger.error(f'Notification cron job failed: {e}')
    
    def send_pending_notifications(self):
        """Send all pending notifications that are due"""
        now = timezone.now()
        pending_notifications = Notification.objects.filter(
            is_sent=False,
            scheduled_for__lte=now
        )
        
        sent_count = 0
        failed_count = 0
        
        for notification in pending_notifications:
            try:
                NotificationService._send_notification(notification)
                sent_count += 1
                self.stdout.write(f"Sent notification: {notification.title}")
            except Exception as e:
                failed_count += 1
                self.stdout.write(f"Failed to send notification {notification.id}: {e}")
                logger.error(f"Failed to send notification {notification.id}: {e}")
        
        if sent_count > 0 or failed_count > 0:
            self.stdout.write(f"Sent {sent_count} notifications, {failed_count} failed")
    
    def schedule_upcoming_notifications(self):
        """Schedule notifications for upcoming bookings"""
        # Get bookings for the next 3 days
        start_date = date.today()
        end_date = start_date + timedelta(days=3)
        
        upcoming_bookings = Booking.objects.filter(
            date__range=[start_date, end_date],
            status__in=['pending', 'confirmed', 'active']
        )
        
        scheduled_count = 0
        
        for booking in upcoming_bookings:
            # Check if notifications are already scheduled
            existing_notifications = Notification.objects.filter(
                booking=booking,
                is_sent=False
            )
            
            if not existing_notifications.exists():
                try:
                    NotificationService.schedule_booking_notifications(booking)
                    scheduled_count += 1
                except Exception as e:
                    self.stdout.write(f"Failed to schedule notifications for booking {booking.id}: {e}")
                    logger.error(f"Failed to schedule notifications for booking {booking.id}: {e}")
        
        if scheduled_count > 0:
            self.stdout.write(f"Scheduled notifications for {scheduled_count} bookings")
