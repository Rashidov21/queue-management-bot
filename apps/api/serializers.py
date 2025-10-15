from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.services.models import Service, Provider
from apps.bookings.models import Booking, Notification
from django.utils import timezone

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    full_name = serializers.ReadOnlyField()
    is_provider = serializers.ReadOnlyField()
    is_client = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'role', 'phone', 'telegram_id', 'is_provider', 
            'is_client', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model"""
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'duration_minutes', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProviderSerializer(serializers.ModelSerializer):
    """Serializer for Provider model"""
    
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Provider
        fields = [
            'id', 'user', 'service', 'service_id', 'user_id',
            'working_days', 'start_time', 'end_time', 'location',
            'is_accepting', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProviderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Provider list"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_duration = serializers.IntegerField(source='service.duration_minutes', read_only=True)
    
    class Meta:
        model = Provider
        fields = [
            'id', 'user_name', 'service_name', 'service_duration',
            'working_days', 'start_time', 'end_time', 'location',
            'is_accepting', 'description'
        ]


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    
    client = UserSerializer(read_only=True)
    provider = ProviderListSerializer(read_only=True)
    provider_id = serializers.IntegerField(write_only=True)
    client_id = serializers.IntegerField(write_only=True)
    duration = serializers.ReadOnlyField()
    end_time = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'client', 'provider', 'provider_id', 'client_id',
            'date', 'time', 'status', 'notes', 'duration', 'end_time',
            'can_be_cancelled', 'is_upcoming', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """Validate booking data"""
        # Check if provider exists and is accepting bookings
        try:
            provider = Provider.objects.get(id=data['provider_id'])
            if not provider.is_accepting:
                raise serializers.ValidationError("Provider is not accepting new bookings")
        except Provider.DoesNotExist:
            raise serializers.ValidationError("Provider not found")
        
        # Check if date is not in the past
        booking_datetime = timezone.datetime.combine(data['date'], data['time'])
        if booking_datetime < timezone.now():
            raise serializers.ValidationError("Cannot book in the past")
        
        # Check if slot is available
        if Booking.objects.filter(
            provider=provider,
            date=data['date'],
            time=data['time'],
            status__in=['pending', 'confirmed', 'active']
        ).exists():
            raise serializers.ValidationError("This time slot is already booked")
        
        return data


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings"""
    
    class Meta:
        model = Booking
        fields = ['provider_id', 'date', 'time', 'notes']
    
    def validate(self, data):
        """Validate booking creation"""
        # Check if provider exists and is accepting bookings
        try:
            provider = Provider.objects.get(id=data['provider_id'])
            if not provider.is_accepting:
                raise serializers.ValidationError("Provider is not accepting new bookings")
        except Provider.DoesNotExist:
            raise serializers.ValidationError("Provider not found")
        
        # Check if date is not in the past
        booking_datetime = timezone.datetime.combine(data['date'], data['time'])
        if booking_datetime < timezone.now():
            raise serializers.ValidationError("Cannot book in the past")
        
        # Check if slot is available
        if Booking.objects.filter(
            provider=provider,
            date=data['date'],
            time=data['time'],
            status__in=['pending', 'confirmed', 'active']
        ).exists():
            raise serializers.ValidationError("This time slot is already booked")
        
        return data


class TimeSlotSerializer(serializers.Serializer):
    """Serializer for available time slots"""
    
    time = serializers.TimeField()
    available = serializers.BooleanField()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'is_read', 'sent_at']
        read_only_fields = ['id', 'sent_at']
