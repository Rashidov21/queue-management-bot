from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
import asyncio

from database.db import async_session_maker
from database.models import Booking, Slot, Provider, User, Service
from config import settings


class NotificationScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.bot = None
    
    def set_bot(self, bot):
        """Set bot instance for sending messages"""
        self.bot = bot
    
    def start(self):
        """Start the scheduler"""
        # Schedule reminder checks every hour
        self.scheduler.add_job(
            self.check_reminders,
            trigger=CronTrigger(minute=0),  # Every hour at minute 0
            id='reminder_check'
        )
        
        # Schedule slot cleanup daily at midnight
        self.scheduler.add_job(
            self.cleanup_expired_slots,
            trigger=CronTrigger(hour=0, minute=0),  # Daily at midnight
            id='slot_cleanup'
        )
        
        self.scheduler.start()
        print("📅 Notification scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("📅 Notification scheduler stopped")
    
    async def check_reminders(self):
        """Check for upcoming appointments and send reminders"""
        if not self.bot:
            return
        
        try:
            # Calculate reminder time window
            now = datetime.now()
            reminder_time = now + timedelta(hours=settings.REMINDER_HOURS_BEFORE)
            reminder_window_start = reminder_time.replace(minute=0, second=0, microsecond=0)
            reminder_window_end = reminder_window_start + timedelta(hours=1)
            
            # Convert to date and time strings for database query
            reminder_date = reminder_window_start.strftime("%Y-%m-%d")
            reminder_time_start = reminder_window_start.strftime("%H:%M")
            reminder_time_end = reminder_window_end.strftime("%H:%M")
            
            async with async_session_maker() as db:
                # Get bookings that need reminders
                result = await db.execute(
                    select(Booking, Slot, Provider, User, Service)
                    .join(Slot, Booking.slot_id == Slot.id)
                    .join(Provider, Slot.provider_id == Provider.id)
                    .join(User, Booking.client_id == User.id)
                    .join(Service, Provider.service_id == Service.id)
                    .where(
                        and_(
                            Booking.status == "active",
                            Slot.date == reminder_date,
                            Slot.time >= reminder_time_start,
                            Slot.time < reminder_time_end
                        )
                    )
                )
                bookings = result.all()
            
            # Send reminders
            for booking, slot, provider, client, service in bookings:
                await self.send_reminder(booking, slot, provider, client, service)
                
        except Exception as e:
            print(f"Error checking reminders: {e}")
    
    async def send_reminder(self, booking, slot, provider, client, service):
        """Send reminder to client and provider"""
        try:
            # Check if we already sent a reminder for this booking
            # (In a real app, you'd track this in the database)
            
            # Send reminder to client
            client_message = f"""
⏰ Reminder!

You have an appointment with {provider.user.full_name} at {slot.time}
Service: {service.name}
Location: {provider.location or 'Check with provider'}

See you soon! 😊
"""
            await self.bot.send_message(client.telegram_id, client_message)
            
            # Send reminder to provider
            provider_message = f"""
⏰ Upcoming Appointment!

Client: {client.full_name}
Time: {slot.time}
Service: {service.name}

Get ready! 😊
"""
            await self.bot.send_message(provider.user.telegram_id, provider_message)
            
            print(f"Sent reminders for booking {booking.id}")
            
        except Exception as e:
            print(f"Failed to send reminder for booking {booking.id}: {e}")
    
    async def cleanup_expired_slots(self):
        """Clean up expired slots and bookings"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M")
            
            async with async_session_maker() as db:
                # Mark expired slots as unavailable
                result = await db.execute(
                    select(Slot)
                    .where(
                        and_(
                            Slot.date < today,
                            Slot.status == "available"
                        )
                    )
                )
                expired_slots = result.scalars().all()
                
                for slot in expired_slots:
                    slot.status = "unavailable"
                
                # Cancel bookings for slots that have passed
                result = await db.execute(
                    select(Booking, Slot)
                    .join(Slot, Booking.slot_id == Slot.id)
                    .where(
                        and_(
                            Booking.status == "active",
                            or_(
                                Slot.date < today,
                                and_(Slot.date == today, Slot.time < current_time)
                            )
                        )
                    )
                )
                expired_bookings = result.all()
                
                for booking, slot in expired_bookings:
                    booking.status = "completed"
                
                await db.commit()
                
                if expired_slots or expired_bookings:
                    print(f"Cleaned up {len(expired_slots)} slots and {len(expired_bookings)} bookings")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    async def send_booking_notification(self, booking, slot, provider, client, service, notification_type="new"):
        """Send booking notifications to provider"""
        try:
            if notification_type == "new":
                message = f"""
📩 New booking received!

👤 Client: {client.full_name}
📅 Date: {slot.date}
⏰ Time: {slot.time}
🔧 Service: {service.name}

Booking confirmed! ✅
"""
            elif notification_type == "cancelled":
                message = f"""
❌ Booking cancelled

👤 Client: {client.full_name}
📅 Date: {slot.date}
⏰ Time: {slot.time}
🔧 Service: {service.name}

The booking has been cancelled.
"""
            
            await self.bot.send_message(provider.user.telegram_id, message)
            
        except Exception as e:
            print(f"Failed to send booking notification: {e}")


# Global scheduler instance
scheduler = NotificationScheduler()
