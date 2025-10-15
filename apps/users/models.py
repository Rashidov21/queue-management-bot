from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('provider', 'Service Provider'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        help_text="User role in the system"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number for contact"
    )
    telegram_id = models.BigIntegerField(
        blank=True,
        null=True,
        unique=True,
        help_text="Telegram user ID"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def full_name(self):
        """Return full name or username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_provider(self):
        """Check if user is a service provider"""
        return self.role == 'provider'
    
    def is_client(self):
        """Check if user is a client"""
        return self.role == 'client'