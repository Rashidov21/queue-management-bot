from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.services.models import Provider


class Booking(models.Model):
    """Bookings made by clients"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings_as_client',
        help_text="Client who made the booking"
    )
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Provider for the booking"
    )
    date = models.DateField(
        help_text="Date of the booking"
    )
    time = models.TimeField(
        help_text="Time of the booking"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes for the booking"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
        unique_together = ['provider', 'date', 'time']
    
    def __str__(self):
        return f"{self.client.full_name} - {self.provider.user.full_name} on {self.date} at {self.time}"
    
    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return self.status in ['pending', 'confirmed', 'active']
    
    def is_upcoming(self):
        """Check if booking is in the future"""
        booking_datetime = timezone.datetime.combine(self.date, self.time)
        if timezone.is_naive(booking_datetime):
            booking_datetime = timezone.make_aware(booking_datetime)
        return booking_datetime > timezone.now()
    
    def get_duration_minutes(self):
        """Get booking duration in minutes"""
        return self.provider.service.duration_minutes
    
    def get_end_time(self):
        """Get booking end time"""
        from datetime import timedelta
        booking_datetime = timezone.datetime.combine(self.date, self.time)
        end_datetime = booking_datetime + timedelta(minutes=self.get_duration_minutes())
        return end_datetime.time()
    
    def save(self, *args, **kwargs):
        """Override save to validate booking"""
        # Validate that client is not a provider
        if self.client.is_provider():
            raise ValueError("Providers cannot book services")
        
        # Validate that provider is accepting bookings
        if not self.provider.is_accepting:
            raise ValueError("Provider is not accepting new bookings")
        
        # Validate date is not in the past
        booking_datetime = timezone.datetime.combine(self.date, self.time)
        if timezone.is_naive(booking_datetime):
            booking_datetime = timezone.make_aware(booking_datetime)
        if booking_datetime < timezone.now():
            raise ValueError("Cannot book in the past")
        
        super().save(*args, **kwargs)


class Notification(models.Model):
    """Notifications for users"""
    
    TYPE_CHOICES = [
        ('booking_reminder', 'Booking Reminder'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_updated', 'Booking Updated'),
        ('provider_message', 'Provider Message'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User to receive notification"
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        help_text="Related booking (if applicable)"
    )
    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        help_text="Type of notification"
    )
    title = models.CharField(
        max_length=200,
        help_text="Notification title"
    )
    message = models.TextField(
        help_text="Notification message"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether notification has been read"
    )
    sent_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"