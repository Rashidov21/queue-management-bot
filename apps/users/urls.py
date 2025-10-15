from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('edit-schedule/', views.edit_schedule_view, name='edit_schedule'),
    path('setup-provider/', views.setup_provider_view, name='setup_provider'),
    path('toggle-availability/', views.toggle_availability_view, name='toggle_availability'),
]
