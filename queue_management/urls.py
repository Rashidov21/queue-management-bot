"""
URL configuration for queue_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import render

def home_view(request):
    """Home page view"""
    return render(request, 'index.html')

def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'Queue Management Bot API',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users/',
            'services': '/api/services/',
            'providers': '/api/providers/',
            'bookings': '/api/bookings/',
            'notifications': '/api/notifications/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('', home_view, name='home'),
    path('users/', include('apps.users.urls')),
    path('services/', include('apps.services.urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('api-info/', api_root, name='api-root'),
]
