from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import date, timedelta, datetime
from .models import User
from apps.services.models import Provider, Service
from apps.bookings.models import Booking, Notification


def home(request):
    """Home page view"""
    # Check if user is coming from Telegram
    telegram_id = request.GET.get('telegram_id')
    if telegram_id:
        try:
            user = User.objects.get(telegram_id=telegram_id)
            login(request, user)
            messages.success(request, f'Xush kelibsiz, {user.full_name}!')
            return redirect('users:profile')
        except User.DoesNotExist:
            messages.error(request, 'Foydalanuvchi topilmadi. Iltimos, bot orqali qayta urinib ko\'ring.')
    
    return render(request, 'index.html')


def telegram_login_view(request):
    """Handle Telegram user login and redirect to profile"""
    telegram_id = request.GET.get('telegram_id')
    
    if not telegram_id:
        messages.error(request, 'Telegram ID topilmadi.')
        return redirect('home')
    
    try:
        user = User.objects.get(telegram_id=telegram_id)
        login(request, user)
        messages.success(request, f'Xush kelibsiz, {user.full_name}!')
        return redirect('users:profile')
    except User.DoesNotExist:
        messages.error(request, 'Foydalanuvchi topilmadi. Iltimos, bot orqali qayta urinib ko\'ring.')
        return redirect('home')


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
        role = request.POST.get('role')
        
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
        messages.info(request, 'Xizmat ko\'rsatuvchi profilingizni to\'ldiring')
        return redirect('users:setup_provider')

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
    
    # Get current month start date
    from datetime import datetime
    current_month_start = datetime.now().replace(day=1).date()
    
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
        # New statistics for people served
        'people_served_today': Booking.objects.filter(
            provider=provider,
            date=today,
            status='completed'
        ).count(),
        'people_served_this_month': Booking.objects.filter(
            provider=provider,
            date__gte=current_month_start,
            status='completed'
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
        messages.info(request, 'Xizmat ko\'rsatuvchi profilingizni to\'ldiring')
        return redirect('users:setup_provider')
    
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
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return render(request, 'users/edit_schedule.html', {'provider': provider, 'days': days})


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
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return render(request, 'users/setup_provider.html', {'services': services, 'days': days})


@login_required
def dashboard_bookings_view(request):
    """Get filtered bookings for dashboard statistics"""
    if not request.user.is_provider():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        return JsonResponse({'error': 'Provider not found'}, status=404)
    
    # Get filter type from request
    filter_type = request.GET.get('filter', 'all')
    page = request.GET.get('page', 1)
    
    # Base queryset
    bookings = Booking.objects.filter(provider=provider).order_by('-created_at')
    
    # Apply filters based on type
    today = timezone.now().date()
    current_month_start = datetime.now().replace(day=1).date()
    
    if filter_type == 'today':
        bookings = bookings.filter(date=today)
        title = "Bugungi buyurtmalar"
    elif filter_type == 'pending':
        bookings = bookings.filter(status='pending')
        title = "Kutilayotgan buyurtmalar"
    elif filter_type == 'confirmed':
        bookings = bookings.filter(status='confirmed')
        title = "Tasdiqlangan buyurtmalar"
    elif filter_type == 'served_today':
        bookings = bookings.filter(date=today, status='completed')
        title = "Bugun xizmat ko'rsatilgan"
    elif filter_type == 'served_month':
        bookings = bookings.filter(date__gte=current_month_start, status='completed')
        title = "Bu oy xizmat ko'rsatilgan"
    else:
        title = "Barcha buyurtmalar"
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_obj = paginator.get_page(page)
    
    # Prepare data for JSON response
    bookings_data = []
    for booking in page_obj:
        bookings_data.append({
            'id': booking.id,
            'client_name': booking.client.full_name,
            'client_phone': booking.client.phone,
            'date': booking.date.strftime('%Y-%m-%d'),
            'time': booking.time.strftime('%H:%M'),
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'notes': booking.notes,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'title': title,
        'bookings': bookings_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count,
    })


@login_required
def profile_edit_view(request):
    """Edit user profile view"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.telegram_username = request.POST.get('telegram_username', user.telegram_username)
        user.save()
        
        messages.success(request, 'Profil muvaffaqiyatli yangilandi')
        return redirect('users:profile')
    
    return render(request, 'users/profile_edit.html')


@login_required
def provider_stats_view(request):
    """Provider statistics view"""
    if not request.user.is_provider():
        messages.error(request, 'Bu sahifaga kirish huquqingiz yo\'q')
        return redirect('home')
    
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.info(request, 'Xizmat ko\'rsatuvchi profilingizni to\'ldiring')
        return redirect('users:setup_provider')
    
    # Get statistics for the last 30 days
    from datetime import timedelta
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    stats = {
        'total_bookings_30_days': Booking.objects.filter(
            provider=provider,
            created_at__gte=thirty_days_ago
        ).count(),
        'completed_bookings_30_days': Booking.objects.filter(
            provider=provider,
            created_at__gte=thirty_days_ago,
            status='completed'
        ).count(),
        'pending_bookings': Booking.objects.filter(
            provider=provider,
            status='pending'
        ).count(),
        'average_rating': 4.5,  # Placeholder for future rating system
    }
    
    return render(request, 'users/provider_stats.html', {
        'provider': provider,
        'stats': stats
    })


@login_required
def notifications_view(request):
    """User notifications view"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-sent_at')[:50]
    
    # Mark notifications as read when viewed
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    return render(request, 'users/notifications.html', {
        'notifications': notifications
    })


@login_required
def user_settings_view(request):
    """User settings view"""
    if request.method == 'POST':
        # Handle settings updates
        user = request.user
        user.phone = request.POST.get('phone', user.phone)
        user.telegram_username = request.POST.get('telegram_username', user.telegram_username)
        user.save()
        
        messages.success(request, 'Sozlamalar muvaffaqiyatli yangilandi')
        return redirect('users:settings')
    
    return render(request, 'users/settings.html')