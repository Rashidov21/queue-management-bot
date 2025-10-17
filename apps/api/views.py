from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from apps.services.models import Service, Provider
from apps.bookings.models import Booking, Notification
from .serializers import (
    UserSerializer, ServiceSerializer, ProviderSerializer, ProviderListSerializer,
    BookingSerializer, BookingCreateSerializer, TimeSlotSerializer, NotificationSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """User registration view for Telegram bot"""
    
    serializer_class = UserSerializer
    permission_classes = []  # No authentication required for registration
    
    def create(self, request, *args, **kwargs):
        """Create new user from Telegram data"""
        telegram_id = request.data.get('telegram_id')
        username = request.data.get('username')
        
        # Check if user already exists
        try:
            existing_user = User.objects.get(telegram_id=telegram_id)
            return Response({
                'id': existing_user.id,
                'username': existing_user.username,
                'telegram_id': existing_user.telegram_id,
                'role': existing_user.role,
                'message': 'User already exists'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            pass
        
        # Create new user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'telegram_id': user.telegram_id,
                'role': user.role,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([])
def telegram_login(request):
    """Login user by telegram_id"""
    telegram_id = request.GET.get('telegram_id')
    
    if not telegram_id:
        return Response({'error': 'telegram_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(telegram_id=telegram_id)
        # Log the user in
        from django.contrib.auth import login
        login(request, user)
        
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'telegram_id': user.telegram_id,
                'role': user.role
            }
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ServiceListView(generics.ListAPIView):
    """List all active services"""
    
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


class ProviderListView(generics.ListAPIView):
    """List all providers"""
    
    queryset = Provider.objects.filter(is_accepting=True).select_related('user', 'service')
    serializer_class = ProviderListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        service_id = self.request.query_params.get('service_id')
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        return queryset


class ProviderDetailView(generics.RetrieveAPIView):
    """Provider detail view"""
    
    queryset = Provider.objects.select_related('user', 'service')
    serializer_class = ProviderSerializer
    permission_classes = [permissions.AllowAny]


class BookingListView(generics.ListCreateAPIView):
    """List and create bookings"""
    
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_provider():
            # Providers see bookings for their services
            return Booking.objects.filter(
                provider__user=user
            ).select_related('client', 'provider__user', 'provider__service')
        else:
            # Clients see their own bookings
            return Booking.objects.filter(
                client=user
            ).select_related('client', 'provider__user', 'provider__service')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Booking detail view"""
    
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_provider():
            return Booking.objects.filter(provider__user=user)
        else:
            return Booking.objects.filter(client=user)
    
    def perform_destroy(self, instance):
        """Cancel booking instead of deleting"""
        if instance.can_be_cancelled():
            instance.status = 'cancelled'
            instance.save()
        else:
            raise ValidationError("Cannot cancel this booking")


class NotificationListView(generics.ListAPIView):
    """List user notifications"""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-sent_at')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def available_slots(request, provider_id):
    """Get available time slots for a provider on a specific date"""
    
    try:
        provider = Provider.objects.get(id=provider_id)
    except Provider.DoesNotExist:
        return Response(
            {'error': 'Provider not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get date from query params
    date_str = request.query_params.get('date')
    if not date_str:
        return Response(
            {'error': 'Date parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        booking_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get available slots
    available_slots = provider.get_available_slots(booking_date)
    
    # Create serializer data
    slots_data = [
        {'time': slot, 'available': True} 
        for slot in available_slots
    ]
    
    serializer = TimeSlotSerializer(slots_data, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    
    try:
        booking = Booking.objects.get(id=booking_id)
        
        # Check permissions
        user = request.user
        if not (booking.client == user or booking.provider.user == user):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not booking.can_be_cancelled():
            return Response(
                {'error': 'Cannot cancel this booking'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        # Create notification
        Notification.objects.create(
            user=booking.client,
            booking=booking,
            type='booking_cancelled',
            title='Booking Cancelled',
            message=f'Your booking with {booking.provider.user.full_name} on {booking.date} at {booking.time} has been cancelled.'
        )
        
        return Response({'message': 'Booking cancelled successfully'})
        
    except Booking.DoesNotExist:
        return Response(
            {'error': 'Booking not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    
    user = request.user
    today = timezone.now().date()
    
    if user.is_provider():
        # Get current month start date
        from datetime import datetime
        current_month_start = datetime.now().replace(day=1).date()
        
        # Provider stats
        total_bookings = Booking.objects.filter(provider__user=user).count()
        today_bookings = Booking.objects.filter(
            provider__user=user,
            date=today,
            status__in=['active', 'confirmed']
        ).count()
        pending_bookings = Booking.objects.filter(
            provider__user=user,
            status='pending'
        ).count()
        people_served_today = Booking.objects.filter(
            provider__user=user,
            date=today,
            status='completed'
        ).count()
        people_served_this_month = Booking.objects.filter(
            provider__user=user,
            date__gte=current_month_start,
            status='completed'
        ).count()
        
        stats = {
            'total_bookings': total_bookings,
            'today_bookings': today_bookings,
            'pending_bookings': pending_bookings,
            'people_served_today': people_served_today,
            'people_served_this_month': people_served_this_month,
            'role': 'provider'
        }
    else:
        # Client stats
        total_bookings = Booking.objects.filter(client=user).count()
        active_bookings = Booking.objects.filter(
            client=user,
            status__in=['pending', 'confirmed', 'active']
        ).count()
        upcoming_bookings = Booking.objects.filter(
            client=user,
            date__gte=today,
            status__in=['pending', 'confirmed', 'active']
        ).count()
        
        stats = {
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'upcoming_bookings': upcoming_bookings,
            'role': 'client'
        }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )