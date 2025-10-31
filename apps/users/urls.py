from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('telegram-login/', views.telegram_login_view, name='telegram_login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile and Dashboard URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/bookings/', views.dashboard_bookings_view, name='dashboard_bookings'),
    
    # Provider Management URLs
    path('provider/setup/', views.setup_provider_view, name='setup_provider'),
    path('provider/schedule/', views.edit_schedule_view, name='edit_schedule'),
    path('provider/availability/', views.toggle_availability_view, name='toggle_availability'),
    path('provider/stats/', views.provider_stats_view, name='provider_stats'),
    
    # User Management URLs
    path('notifications/', views.notifications_view, name='notifications'),
    path('settings/', views.user_settings_view, name='settings'),
]



