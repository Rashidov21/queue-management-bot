from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import date, timedelta
from .models import Booking, Notification
from apps.services.models import Provider
from apps.users.models import User


@login_required
def booking_list_view(request):
    """List user's bookings"""
    if request.user.is_provider():
        # Provider sees bookings for their services
        bookings = Booking.objects.filter(
            provider__user=request.user
        ).select_related('client', 'provider__service').order_by('-created_at')
    else:
        # Client sees their own bookings
        bookings = Booking.objects.filter(
            client=request.user
        ).select_related('provider__user', 'provider__service').order_by('-created_at')
    
    return render(request, 'bookings/list.html', {'bookings': bookings})


@login_required
def booking_create_view(request, provider_id):
    """Create a new booking"""
    provider = get_object_or_404(Provider, id=provider_id)
    
    if request.method == 'POST':
        booking_date = request.POST.get('date')
        booking_time = request.POST.get('time')
        notes = request.POST.get('notes', '')
        
        # Validate date is not in the past
        try:
            booking_datetime = timezone.datetime.strptime(f"{booking_date} {booking_time}", '%Y-%m-%d %H:%M')
            if booking_datetime < timezone.now():
                messages.error(request, 'O\'tgan vaqtni tanlay olmaysiz')
                return render(request, 'bookings/create.html', {'provider': provider})
        except ValueError:
            messages.error(request, 'Noto\'g\'ri sana yoki vaqt formati')
            return render(request, 'bookings/create.html', {'provider': provider})
        
        # Check if slot is available
        existing_booking = Booking.objects.filter(
            provider=provider,
            date=booking_date,
            time=booking_time,
            status__in=['pending', 'confirmed', 'active']
        ).exists()
        
        if existing_booking:
            messages.error(request, 'Bu vaqt band')
            return render(request, 'bookings/create.html', {'provider': provider})
        
        # Create booking
        booking = Booking.objects.create(
            client=request.user,
            provider=provider,
            date=booking_date,
            time=booking_time,
            notes=notes,
            status='pending'
        )
        
        # Create notification for provider
        Notification.objects.create(
            user=provider.user,
            booking=booking,
            type='booking_confirmed',
            title='Yangi buyurtma',
            message=f'{request.user.full_name} sizga buyurtma berdi. Sana: {booking_date}, Vaqt: {booking_time}'
        )
        
        messages.success(request, 'Buyurtma muvaffaqiyatli yaratildi!')
        return redirect('bookings:success', booking_id=booking.id)
    
    return render(request, 'bookings/create.html', {'provider': provider})


@login_required
def booking_success_view(request, booking_id):
    """Booking success page"""
    booking = get_object_or_404(Booking, id=booking_id, client=request.user)
    return render(request, 'bookings/success.html', {'booking': booking})


@login_required
@require_POST
@csrf_exempt
def booking_cancel_view(request, booking_id):
    """Cancel a booking"""
    try:
        booking = Booking.objects.get(id=booking_id)
        
        # Check permissions
        if booking.client != request.user and booking.provider.user != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        if not booking.can_be_cancelled():
            return JsonResponse({'success': False, 'error': 'Cannot cancel this booking'})
        
        booking.status = 'cancelled'
        booking.save()
        
        # Create notification
        Notification.objects.create(
            user=booking.client if booking.provider.user == request.user else booking.provider.user,
            booking=booking,
            type='booking_cancelled',
            title='Buyurtma bekor qilindi',
            message=f'Buyurtma bekor qilindi. Sana: {booking.date}, Vaqt: {booking.time}'
        )
        
        return JsonResponse({'success': True})
        
    except Booking.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Booking not found'})


@login_required
@require_POST
@csrf_exempt
def booking_confirm_view(request, booking_id):
    """Confirm a booking (for providers)"""
    if not request.user.is_provider():
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        booking = Booking.objects.get(id=booking_id, provider__user=request.user)
        
        if booking.status != 'pending':
            return JsonResponse({'success': False, 'error': 'Booking is not pending'})
        
        booking.status = 'confirmed'
        booking.save()
        
        # Create notification for client
        Notification.objects.create(
            user=booking.client,
            booking=booking,
            type='booking_confirmed',
            title='Buyurtma tasdiqlandi',
            message=f'Buyurtmangiz tasdiqlandi. Sana: {booking.date}, Vaqt: {booking.time}'
        )
        
        return JsonResponse({'success': True})
        
    except Booking.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Booking not found'})


@login_required
def booking_detail_view(request, booking_id):
    """Booking detail view"""
    if request.user.is_provider():
        booking = get_object_or_404(Booking, id=booking_id, provider__user=request.user)
    else:
        booking = get_object_or_404(Booking, id=booking_id, client=request.user)
    
    return render(request, 'bookings/detail.html', {'booking': booking})