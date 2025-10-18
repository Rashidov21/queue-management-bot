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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

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

@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Telegram webhook endpoint"""
    try:
        # Parse the JSON data from Telegram
        data = json.loads(request.body.decode('utf-8'))
        
        # Log the incoming webhook for debugging
        print(f"Telegram webhook received: {data}")
        
        # Process the Telegram update
        from apps.bot.handlers import process_telegram_update
        result = process_telegram_update(data)
        
        return JsonResponse({'status': 'ok', 'result': result})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Webhook error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('webhook/', telegram_webhook, name='telegram_webhook'),
    path('', home_view, name='home'),
    path('users/', include('apps.users.urls')),
    path('services/', include('apps.services.urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('api-info/', api_root, name='api-root'),
]
