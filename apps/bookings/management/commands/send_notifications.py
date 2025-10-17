from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bookings.notification_service import NotificationService
from apps.bookings.models import Booking, Notification
from apps.services.models import Provider
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send pending notifications and schedule new ones'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually sending notifications',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No notifications will be sent'))
        
        # Send pending notifications
        self.send_pending_notifications(dry_run)
        
        # Schedule new notifications for today's bookings
        self.schedule_today_notifications(dry_run)
        
        # Schedule provider notifications
        self.schedule_provider_notifications(dry_run)
    
    def send_pending_notifications(self, dry_run):
        """Send all pending notifications that are due"""
        now = timezone.now()
        pending_notifications = Notification.objects.filter(
            is_sent=False,
            scheduled_for__lte=now
        )
        
        self.stdout.write(f"Found {pending_notifications.count()} pending notifications")
        
        for notification in pending_notifications:
            if dry_run:
                self.stdout.write(f"Would send: {notification.title} to {notification.user.telegram_username}")
            else:
                try:
                    NotificationService._send_notification(notification)
                    self.stdout.write(
                        self.style.SUCCESS(f"Sent: {notification.title} to {notification.user.telegram_username}")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to send {notification.title}: {e}")
                    )
    
    def schedule_today_notifications(self, dry_run):
        """Schedule notifications for today's bookings"""
        today = date.today()
        today_bookings = Booking.objects.filter(
            date=today,
            status__in=['pending', 'confirmed', 'active']
        )
        
        self.stdout.write(f"Found {today_bookings.count()} bookings for today")
        
        for booking in today_bookings:
            if dry_run:
                self.stdout.write(f"Would schedule notifications for booking {booking.id}")
            else:
                try:
                    NotificationService.schedule_booking_notifications(booking)
                    self.stdout.write(f"Scheduled notifications for booking {booking.id}")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to schedule notifications for booking {booking.id}: {e}")
                    )
    
    def schedule_provider_notifications(self, dry_run):
        """Schedule provider notifications for today"""
        today = date.today()
        providers = Provider.objects.filter(
            user__telegram_username__isnull=False
        ).distinct()
        
        for provider in providers:
            if dry_run:
                self.stdout.write(f"Would schedule provider notifications for {provider.user.full_name}")
            else:
                try:
                    NotificationService.schedule_today_queues_notification(provider, today)
                    self.stdout.write(f"Scheduled provider notifications for {provider.user.full_name}")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to schedule provider notifications for {provider.user.full_name}: {e}")
                    )
