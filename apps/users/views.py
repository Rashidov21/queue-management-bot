from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from datetime import date, timedelta
from .models import User
from apps.services.models import Provider, Service
from apps.bookings.models import Booking, Notification


def home(request):
    """Home page view"""
    return render(request, 'index.html')


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Xush kelibsiz, {user.full_name}!')
            
            # Redirect based on user role
            if user.is_provider():
                return redirect('users:dashboard')
            else:
                return redirect('services:list')
        else:
            messages.error(request, 'Noto\'g\'ri foydalanuvchi nomi yoki parol')
    
    return render(request, 'users/login.html')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        role = request.POST.get('role', 'client')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Parollar mos kelmaydi')
            return render(request, 'users/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu foydalanuvchi nomi allaqachon mavjud')
            return render(request, 'users/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Bu email allaqachon mavjud')
            return render(request, 'users/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role
        )
        
        login(request, user)
        messages.success(request, f'Ro\'yxatdan muvaffaqiyatli o\'tdingiz, {user.full_name}!')
        
        if user.is_provider():
            return redirect('users:dashboard')
        else:
            return redirect('services:list')
    
    return render(request, 'users/register.html')


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'Muvaffaqiyatli chiqdingiz')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        
        messages.success(request, 'Profil muvaffaqiyatli yangilandi')
        return redirect('users:profile')
    
    return render(request, 'users/profile.html')


@login_required
def dashboard_view(request):
    """Provider dashboard view"""
    if not request.user.is_provider():
        messages.error(request, 'Bu sahifaga kirish huquqingiz yo\'q')
        return redirect('home')
    
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Siz hali xizmat ko\'rsatuvchi sifatida ro\'yxatdan o\'tmagansiz')
        return redirect('users:profile')
    
    # Get statistics
    today = timezone.now().date()
    
    # Today's bookings
    today_bookings = Booking.objects.filter(
        provider=provider,
        date=today,
        status__in=['pending', 'confirmed', 'active']
    ).order_by('time')
    
    # Upcoming bookings
    upcoming_bookings = Booking.objects.filter(
        provider=provider,
        date__gt=today,
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time')[:10]
    
    # Statistics
    stats = {
        'total_bookings': Booking.objects.filter(provider=provider).count(),
        'today_bookings': today_bookings.count(),
        'pending_bookings': Booking.objects.filter(
            provider=provider,
            status='pending'
        ).count(),
        'confirmed_bookings': Booking.objects.filter(
            provider=provider,
            status='confirmed'
        ).count(),
    }
    
    context = {
        'provider': provider,
        'today_bookings': today_bookings,
        'upcoming_bookings': upcoming_bookings,
        'stats': stats,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def edit_schedule_view(request):
    """Edit provider schedule view"""
    if not request.user.is_provider():
        messages.error(request, 'Bu sahifaga kirish huquqingiz yo\'q')
        return redirect('home')
    
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Siz hali xizmat ko\'rsatuvchi sifatida ro\'yxatdan o\'tmagansiz')
        return redirect('users:profile')
    
    if request.method == 'POST':
        working_days = request.POST.getlist('working_days')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        provider.working_days = working_days
        provider.start_time = start_time
        provider.end_time = end_time
        provider.save()
        
        messages.success(request, 'Ish jadvali muvaffaqiyatli yangilandi')
        return redirect('users:dashboard')
    
    return render(request, 'users/edit_schedule.html', {'provider': provider})


@login_required
def toggle_availability_view(request):
    """Toggle provider availability"""
    if not request.user.is_provider():
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        provider = request.user.provider_profile
        provider.is_accepting = not provider.is_accepting
        provider.save()
        
        return JsonResponse({
            'success': True,
            'is_accepting': provider.is_accepting
        })
    except Provider.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Provider not found'})


@login_required
def setup_provider_view(request):
    """Setup provider profile for new providers"""
    if request.user.is_provider():
        try:
            provider = request.user.provider_profile
            messages.info(request, 'Siz allaqachon xizmat ko\'rsatuvchi sifatida ro\'yxatdan o\'tgansiz')
            return redirect('users:dashboard')
        except Provider.DoesNotExist:
            pass
    
    if request.method == 'POST':
        service_id = request.POST.get('service')
        description = request.POST.get('description')
        location = request.POST.get('location')
        working_days = request.POST.getlist('working_days')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        try:
            service = Service.objects.get(id=service_id)
            provider = Provider.objects.create(
                user=request.user,
                service=service,
                description=description,
                location=location,
                working_days=working_days,
                start_time=start_time,
                end_time=end_time
            )
            
            # Update user role
            request.user.role = 'provider'
            request.user.save()
            
            messages.success(request, 'Xizmat ko\'rsatuvchi profili muvaffaqiyatli yaratildi')
            return redirect('users:dashboard')
        except Service.DoesNotExist:
            messages.error(request, 'Tanlangan xizmat topilmadi')
    
    services = Service.objects.filter(is_active=True)
    return render(request, 'users/setup_provider.html', {'services': services})