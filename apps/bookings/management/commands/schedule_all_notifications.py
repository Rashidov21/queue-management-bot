from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bookings.notification_service import NotificationService
from apps.bookings.models import Booking
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Schedule notifications for all existing bookings'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Number of days ahead to schedule notifications (default: 7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually scheduling notifications',
        )
    
    def handle(self, *args, **options):
        days_ahead = options['days_ahead']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No notifications will be scheduled'))
        
        # Get bookings for the next N days
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        
        bookings = Booking.objects.filter(
            date__range=[start_date, end_date],
            status__in=['pending', 'confirmed', 'active']
        ).order_by('date', 'time')
        
        self.stdout.write(f"Found {bookings.count()} bookings to schedule notifications for")
        
        scheduled_count = 0
        skipped_count = 0
        
        for booking in bookings:
            if not booking.client.telegram_username:
                self.stdout.write(f"Skipping booking {booking.id} - no Telegram username for client")
                skipped_count += 1
                continue
            
            if dry_run:
                self.stdout.write(f"Would schedule notifications for booking {booking.id} ({booking.date} {booking.time})")
            else:
                try:
                    # Cancel existing notifications first
                    NotificationService.cancel_booking_notifications(booking)
                    
                    # Schedule new notifications
                    NotificationService.schedule_booking_notifications(booking)
                    scheduled_count += 1
                    self.stdout.write(f"Scheduled notifications for booking {booking.id}")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to schedule notifications for booking {booking.id}: {e}")
                    )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully scheduled notifications for {scheduled_count} bookings. "
                    f"Skipped {skipped_count} bookings."
                )
            )
        else:
            self.stdout.write(f"Would schedule notifications for {bookings.count()} bookings")
