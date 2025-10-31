from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Service URLs
    path('', views.service_list_view, name='list'),
    path('<int:service_id>/', views.service_detail_view, name='detail'),
    
    # Provider URLs
    path('providers/', views.provider_list_view, name='provider_list'),
    path('providers/<int:provider_id>/', views.provider_detail_view, name='provider_detail'),
    path('providers/<int:provider_id>/slots/', views.available_slots_view, name='available_slots'),
    path('providers/<int:provider_id>/book/', views.provider_booking_view, name='provider_booking'),
]



