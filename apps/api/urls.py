from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # User endpoints
    path('users/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('users/telegram-login/', views.telegram_login, name='telegram-login'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Service endpoints
    path('services/', views.ServiceListView.as_view(), name='service-list'),
    
    # Provider endpoints
    path('providers/', views.ProviderListView.as_view(), name='provider-list'),
    path('providers/<int:pk>/', views.ProviderDetailView.as_view(), name='provider-detail'),
    path('providers/<int:provider_id>/slots/', views.available_slots, name='available-slots'),
    
    # Booking endpoints
    path('bookings/', views.BookingListView.as_view(), name='booking-list'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    
    # Notification endpoints
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    
    # Dashboard endpoints
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]
