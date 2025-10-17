# Queue Management Bot Notification System

This document describes the automated notification system for the queue management bot.

## Overview

The notification system sends automated reminders to both customers and service providers about upcoming queue appointments through Telegram.

## Customer Notifications

Customers receive notifications at the following intervals before their appointment:

- **72 hours** before appointment
- **36 hours** before appointment  
- **24 hours** before appointment
- **3 hours** before appointment
- **1 hour** before appointment

### Customer Notification Types

1. **Queue Reminder 72h** - Initial reminder with 72 hours remaining
2. **Queue Reminder 36h** - Second reminder with 36 hours remaining
3. **Queue Reminder 24h** - Third reminder with 24 hours remaining
4. **Queue Reminder 3h** - Final reminder with 3 hours remaining
5. **Queue Reminder 1h** - Last reminder with 1 hour remaining

## Provider Notifications

Service providers receive notifications about:

1. **Next Queue** - 1 hour before their next appointment
2. **Today's Queues** - Overview of all appointments for the day

### Provider Notification Types

1. **Provider Next Queue** - Notification about the next upcoming appointment
2. **Provider Today Queues** - Summary of all appointments for today

## Technical Implementation

### Models

The system uses the `Notification` model with the following key fields:

- `type` - Type of notification (queue_reminder_72h, provider_next_queue, etc.)
- `user` - User receiving the notification
- `booking` - Related booking (if applicable)
- `scheduled_for` - When the notification should be sent
- `is_sent` - Whether the notification has been sent
- `sent_via` - How the notification was sent (telegram, email, etc.)

### Services

#### NotificationService

Main service for managing notifications:

- `schedule_booking_notifications(booking)` - Schedule all notifications for a booking
- `send_pending_notifications()` - Send all pending notifications
- `cancel_booking_notifications(booking)` - Cancel notifications for a booking
- `update_booking_notifications(booking)` - Update notifications when booking changes

#### TelegramService

Handles sending messages via Telegram:

- `send_message(chat_id, message)` - Send a basic message
- `send_booking_confirmation(booking)` - Send booking confirmation
- `send_booking_reminder(booking, hours_remaining)` - Send reminder
- `send_provider_notification(provider, message)` - Send provider notification

### Management Commands

#### send_notifications.py

Sends pending notifications and schedules new ones:

```bash
python manage.py send_notifications
python manage.py send_notifications --dry-run
```

#### schedule_all_notifications.py

Schedules notifications for all existing bookings:

```bash
python manage.py schedule_all_notifications
python manage.py schedule_all_notifications --days-ahead 7
python manage.py schedule_all_notifications --dry-run
```

#### cron_notifications.py

Cron job to run every 5 minutes:

```bash
python manage.py cron_notifications
```

### Celery Tasks (Optional)

If Celery is configured, the following tasks are available:

- `send_pending_notifications` - Send pending notifications
- `schedule_daily_notifications` - Schedule daily notifications
- `send_booking_confirmation(booking_id)` - Send booking confirmation
- `send_booking_cancellation(booking_id)` - Send booking cancellation

## Setup Instructions

### 1. Environment Variables

Add the following to your `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 2. Database Migration

Run migrations to update the notification model:

```bash
python manage.py makemigrations bookings
python manage.py migrate
```

### 3. Schedule Existing Bookings

Schedule notifications for existing bookings:

```bash
python manage.py schedule_all_notifications
```

### 4. Set Up Cron Job

Add to your crontab to run every 5 minutes:

```bash
*/5 * * * * cd /path/to/your/project && python manage.py cron_notifications
```

### 5. Celery Setup (Optional)

If using Celery, add to your `settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'send-notifications': {
        'task': 'apps.bookings.tasks.send_pending_notifications',
        'schedule': 300.0,  # Every 5 minutes
    },
    'schedule-daily-notifications': {
        'task': 'apps.bookings.tasks.schedule_daily_notifications',
        'schedule': 86400.0,  # Daily
    },
}
```

## Notification Flow

### When a Booking is Created

1. Booking is saved to database
2. `NotificationService.schedule_booking_notifications()` is called
3. All customer reminder notifications are scheduled
4. Provider next queue notification is scheduled

### When a Booking is Updated

1. Existing notifications are cancelled
2. New notifications are scheduled with updated information

### When a Booking is Cancelled

1. All scheduled notifications are cancelled
2. Cancellation notification is sent immediately

### Daily Processing

1. Cron job runs every 5 minutes
2. Pending notifications are sent
3. New notifications are scheduled for upcoming bookings
4. Provider daily notifications are scheduled

## Message Templates

### Customer Reminder Template

```
⏰ Navbat eslatmasi

📅 Sana: 2024-01-15
🕐 Vaqt: 14:30
👤 Xizmat ko'rsatuvchi: John Doe
📍 Manzil: Toshkent shahar
⏳ Qolgan vaqt: 24 soat

Navbat vaqtida kelishingizni so'raymiz!
```

### Provider Next Queue Template

```
🔔 Keyingi navbat eslatmasi

📅 Sana: 2024-01-15
🕐 Vaqt: 14:30
👤 Mijoz: Jane Smith
📞 Telefon: +998901234567
📝 Izoh: Tez keling

1 soatdan keyin navbat boshlanadi!
```

### Provider Today's Queues Template

```
📋 Bugungi navbatlar

👤 Xizmat ko'rsatuvchi: John Doe
📅 Sana: 2024-01-15

✅ 09:00 - Jane Smith
⏳ 10:30 - Bob Johnson
✅ 14:00 - Alice Brown

Bugungi navbatlar ro'yxati!
```

## Troubleshooting

### Common Issues

1. **Notifications not being sent**
   - Check Telegram bot token is correct
   - Verify user has Telegram username
   - Check cron job is running
   - Review logs for errors

2. **Duplicate notifications**
   - Check if notifications are being scheduled multiple times
   - Verify booking save method is not called multiple times

3. **Missing notifications**
   - Check if booking has Telegram username
   - Verify notification scheduling logic
   - Check if notifications are being cancelled unexpectedly

### Logging

Enable detailed logging by adding to `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'notifications.log',
        },
    },
    'loggers': {
        'apps.bookings.notification_service': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.bookings.telegram_service': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Testing

### Manual Testing

1. Create a test booking
2. Check if notifications are scheduled
3. Run `python manage.py send_notifications --dry-run`
4. Verify notification content

### Automated Testing

```python
from django.test import TestCase
from apps.bookings.notification_service import NotificationService
from apps.bookings.models import Booking

class NotificationTestCase(TestCase):
    def test_schedule_notifications(self):
        # Create test booking
        booking = Booking.objects.create(...)
        
        # Schedule notifications
        NotificationService.schedule_booking_notifications(booking)
        
        # Verify notifications were created
        notifications = Notification.objects.filter(booking=booking)
        self.assertEqual(notifications.count(), 5)  # 5 customer reminders
```

## Monitoring

### Key Metrics to Monitor

1. **Notification delivery rate** - Percentage of successfully sent notifications
2. **Scheduling accuracy** - Notifications sent at correct times
3. **Error rate** - Failed notification attempts
4. **User engagement** - Response to notifications

### Health Checks

Add health check endpoints to monitor:

- Notification queue size
- Failed notification count
- Telegram API connectivity
- Database notification status

## Security Considerations

1. **Telegram Bot Token** - Keep secure and rotate regularly
2. **User Privacy** - Only send notifications to users who have opted in
3. **Rate Limiting** - Respect Telegram API rate limits
4. **Data Protection** - Ensure notification content doesn't expose sensitive data

## Future Enhancements

1. **Email Notifications** - Add email as alternative to Telegram
2. **SMS Notifications** - Add SMS support for critical reminders
3. **Push Notifications** - Mobile app push notifications
4. **Custom Templates** - Allow providers to customize notification templates
5. **Analytics** - Track notification effectiveness and user engagement
