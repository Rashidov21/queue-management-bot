from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Booking, Notification


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for Booking model"""
    
    list_display = ('client', 'provider', 'date', 'time', 'status_display', 'duration', 'created_at')
    list_filter = ('status', 'date', 'created_at', 'provider__service')
    search_fields = ('client__username', 'client__first_name', 'client__last_name', 
                    'provider__user__username', 'provider__user__first_name')
    ordering = ('-created_at',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('client', 'provider', 'date', 'time', 'status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'active': 'green',
            'completed': 'purple',
            'cancelled': 'red',
            'no_show': 'darkred',
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                         color, obj.get_status_display())
    status_display.short_description = 'Status'
    
    def duration(self, obj):
        """Display booking duration"""
        return f"{obj.get_duration_minutes()} minutes"
    duration.short_description = 'Duration'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'client', 'provider__user', 'provider__service'
        )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model"""
    
    list_display = ('user', 'type', 'title', 'is_read', 'sent_at')
    list_filter = ('type', 'is_read', 'sent_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'title', 'message')
    ordering = ('-sent_at',)
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'booking', 'type', 'title', 'message', 'is_read')
        }),
        ('Timestamps', {
            'fields': ('sent_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('sent_at',)
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user', 'booking')