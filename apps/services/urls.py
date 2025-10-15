from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list_view, name='list'),
    path('<int:service_id>/', views.service_detail_view, name='detail'),
    path('provider/<int:provider_id>/', views.provider_detail_view, name='provider_detail'),
    path('provider/<int:provider_id>/slots/', views.available_slots_view, name='available_slots'),
]
