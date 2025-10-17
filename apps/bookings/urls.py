from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list_view, name='list'),
    path('create/<int:provider_id>/', views.booking_create_view, name='create'),
    path('success/<int:booking_id>/', views.booking_success_view, name='success'),
    path('<int:booking_id>/', views.booking_detail_view, name='detail'),
    path('<int:booking_id>/cancel/', views.booking_cancel_view, name='cancel'),
    path('<int:booking_id>/confirm/', views.booking_confirm_view, name='confirm'),
]
