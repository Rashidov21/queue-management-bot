from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import date, time, timedelta
from .models import Booking, Notification
from apps.services.models import Provider
from apps.users.models import User


@login_required
def booking_list_view(request):
    """List user's bookings"""
    if request.user.is_provider():
        # Provider sees bookings for their services
        bookings = Booking.objects.filter(
            provider__user=request.user,
        ).select_related('client', 'provider__service').order_by('-date')
    else:
        # Client sees their own bookings
        bookings = Booking.objects.filter(
            client=request.user
        ).select_related('provider__user', 'provider__service').order_by('-created_at')
        

    return render(request, 'bookings/list.html', {'bookings': bookings, 'today': date.today().day})


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
            if timezone.is_naive(booking_datetime):
                booking_datetime = timezone.make_aware(booking_datetime)
            if booking_datetime < timezone.now():
                messages.error(request, 'O\'tgan vaqtni tanlay olmaysiz')
                return render(request, 'bookings/create.html', {'provider': provider})
        except ValueError:
            messages.error(request, 'Noto\'g\'ri sana yoki vaqt formati')
            return render(request, 'bookings/create.html', {'provider': provider})
        
        # Validate working days
        booking_date_obj = date.fromisoformat(booking_date)
        day_name = booking_date_obj.strftime('%A').lower()
        if day_name not in provider.working_days:
            messages.error(request, f'Bu kun {provider.user.full_name} uchun ish kuni emas')
            return render(request, 'bookings/create.html', {'provider': provider})
        
        # Validate working hours
        booking_time_obj = time.fromisoformat(booking_time)
        if booking_time_obj < provider.start_time or booking_time_obj >= provider.end_time:
            messages.error(request, f'Bu vaqt {provider.user.full_name} uchun ish vaqti emas ({provider.start_time} - {provider.end_time})')
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
            date=date.fromisoformat(booking_date),
            time=time.fromisoformat(booking_time),
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


@login_required
@require_POST
@csrf_exempt
def booking_complete_view(request, booking_id):
    """Complete a booking (for providers)"""
    if not request.user.is_provider():
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        booking = Booking.objects.get(id=booking_id, provider__user=request.user)
        
        if booking.status not in ['confirmed', 'active']:
            return JsonResponse({'success': False, 'error': 'Booking cannot be completed'})
        
        booking.status = 'completed'
        booking.save()
        
        # Create notification for client
        Notification.objects.create(
            user=booking.client,
            booking=booking,
            type='booking_completed',
            title='Xizmat yakunlandi',
            message=f'Xizmat muvaffaqiyatli yakunlandi. Rahmat!'
        )
        
        return JsonResponse({'success': True})
        
    except Booking.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Booking not found'})


@login_required
def booking_reschedule_view(request, booking_id):
    """Reschedule a booking"""
    if request.user.is_provider():
        booking = get_object_or_404(Booking, id=booking_id, provider__user=request.user)
    else:
        booking = get_object_or_404(Booking, id=booking_id, client=request.user)
    
    if request.method == 'POST':
        new_date = request.POST.get('date')
        new_time = request.POST.get('time')
        reason = request.POST.get('reason', '')
        
        try:
            booking.date = date.fromisoformat(new_date)
            booking.time = time.fromisoformat(new_time)
            booking.save()
            
            # Create notification
            Notification.objects.create(
                user=booking.client if booking.provider.user == request.user else booking.provider.user,
                booking=booking,
                type='booking_updated',
                title='Buyurtma qayta belgilandi',
                message=f'Buyurtma yangi vaqtga ko\'chirildi: {new_date} {new_time}'
            )
            
            messages.success(request, 'Buyurtma muvaffaqiyatli qayta belgilandi')
            return redirect('bookings:detail', booking_id=booking.id)
        except Exception as e:
            messages.error(request, f'Xatolik yuz berdi: {str(e)}')
    
    return render(request, 'bookings/reschedule.html', {'booking': booking})


@login_required
def booking_calendar_view(request):
    """Booking calendar view"""
    if request.user.is_provider():
        bookings = Booking.objects.filter(
            provider__user=request.user
        ).select_related('client', 'provider__service')
    else:
        bookings = Booking.objects.filter(
            client=request.user
        ).select_related('provider__user', 'provider__service')
    
    return render(request, 'bookings/calendar.html', {'bookings': bookings})


@login_required
def booking_export_view(request):
    """Export bookings to CSV"""
    if request.user.is_provider():
        bookings = Booking.objects.filter(
            provider__user=request.user
        ).select_related('client', 'provider__service')
    else:
        bookings = Booking.objects.filter(
            client=request.user
        ).select_related('provider__user', 'provider__service')
    
    # Create CSV response
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Client', 'Provider', 'Service', 'Date', 'Time', 'Status', 'Notes'])
    
    for booking in bookings:
        if request.user.is_provider():
            writer.writerow([
                booking.id,
                booking.client.full_name,
                booking.provider.user.full_name,
                booking.provider.service.name,
                booking.date,
                booking.time,
                booking.get_status_display(),
                booking.notes
            ])
        else:
            writer.writerow([
                booking.id,
                booking.client.full_name,
                booking.provider.user.full_name,
                booking.provider.service.name,
                booking.date,
                booking.time,
                booking.get_status_display(),
                booking.notes
            ])
    
    return response