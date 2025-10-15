from django.db import models
from django.utils import timezone
from apps.users.models import User


class Service(models.Model):
    """Service types offered by providers"""
    
    name = models.CharField(
        max_length=100,
        help_text="Name of the service"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the service"
    )
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Duration of the service in minutes"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the service is available"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Provider(models.Model):
    """Service providers"""
    
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='provider_profile',
        help_text="User account for this provider"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='providers',
        help_text="Service offered by this provider"
    )
    working_days = models.JSONField(
        default=list,
        help_text="List of working days (e.g., ['monday', 'tuesday'])"
    )
    start_time = models.TimeField(
        help_text="Start time of working hours"
    )
    end_time = models.TimeField(
        help_text="End time of working hours"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Provider location"
    )
    is_accepting = models.BooleanField(
        default=True,
        help_text="Whether provider is accepting new bookings"
    )
    description = models.TextField(
        blank=True,
        help_text="Provider description"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'providers'
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.service.name}"
    
    def get_available_slots(self, date):
        """Get available time slots for a given date"""
        from apps.bookings.models import Booking
        
        # Check if date is a working day
        day_name = date.strftime('%A').lower()
        if day_name not in self.working_days:
            return []
        
        # Get existing bookings for this date
        existing_bookings = Booking.objects.filter(
            provider=self,
            date=date,
            status__in=['active', 'confirmed']
        ).values_list('time', flat=True)
        
        # Generate available slots
        available_slots = []
        current_time = self.start_time
        
        while current_time < self.end_time:
            # Convert time to datetime for comparison
            slot_datetime = timezone.datetime.combine(date, current_time)
            
            # Check if slot is available and not in the past
            if timezone.is_naive(slot_datetime):
                slot_datetime = timezone.make_aware(slot_datetime)
            if (current_time not in existing_bookings and 
                slot_datetime > timezone.now()):
                available_slots.append(current_time)
            
            # Add service duration to get next slot
            from datetime import timedelta
            current_time = (timezone.datetime.combine(date, current_time) + 
                          timedelta(minutes=self.service.duration_minutes)).time()
        
        return available_slots