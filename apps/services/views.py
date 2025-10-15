from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from .models import Service, Provider


def service_list_view(request):
    """List all available services"""
    services = Service.objects.filter(is_active=True)
    return render(request, 'services/list.html', {'services': services})


def service_detail_view(request, service_id):
    """Service detail with providers"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    providers = Provider.objects.filter(
        service=service,
        is_accepting=True
    ).select_related('user')
    
    return render(request, 'services/detail.html', {
        'service': service,
        'providers': providers
    })


def provider_detail_view(request, provider_id):
    """Provider detail view"""
    provider = get_object_or_404(Provider, id=provider_id)
    
    # Get next 7 days for calendar
    today = date.today()
    next_week = [today + timedelta(days=i) for i in range(7)]
    
    return render(request, 'services/provider_detail.html', {
        'provider': provider,
        'next_week': next_week
    })


@login_required
def available_slots_view(request, provider_id):
    """Get available time slots for a provider"""
    provider = get_object_or_404(Provider, id=provider_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date parameter is required'})
    
    try:
        booking_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'})
    
    # Get available slots
    available_slots = provider.get_available_slots(booking_date)
    
    # Format slots
    slots = [{'time': slot.strftime('%H:%M'), 'available': True} for slot in available_slots]
    
    return JsonResponse(slots, safe=False)