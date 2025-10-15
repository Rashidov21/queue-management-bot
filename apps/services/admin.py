from django.contrib import admin
from django.utils.html import format_html
from .models import Service, Provider


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin configuration for Service model"""
    
    list_display = ('name', 'duration_minutes', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'duration_minutes', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).prefetch_related('providers')


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    """Admin configuration for Provider model"""
    
    list_display = ('user', 'service', 'location', 'working_days_display', 'is_accepting', 'created_at')
    list_filter = ('service', 'is_accepting', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'location')
    ordering = ('user__username',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'service', 'description', 'location')
        }),
        ('Working Hours', {
            'fields': ('working_days', 'start_time', 'end_time', 'is_accepting')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def working_days_display(self, obj):
        """Display working days in a readable format"""
        if obj.working_days:
            days = ', '.join([day.capitalize() for day in obj.working_days])
            return format_html('<span style="color: green;">{}</span>', days)
        return format_html('<span style="color: red;">No days set</span>')
    working_days_display.short_description = 'Working Days'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user', 'service')