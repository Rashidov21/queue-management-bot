#!/usr/bin/env python3
"""
Startup script for PythonAnywhere
This script initializes the application and sets up necessary components
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queue_management.settings')

# Initialize Django
django.setup()

# Import after Django setup
from django.core.management import execute_from_command_line
from django.conf import settings

def main():
    """Main startup function"""
    print("🚀 Starting Queue Management Bot...")
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ manage.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check Django configuration
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'check'])
        print("✅ Django configuration is valid")
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        sys.exit(1)
    
    # Check database
    try:
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection is working")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        sys.exit(1)
    
    # Check Telegram bot configuration
    if hasattr(settings, 'TELEGRAM_BOT_TOKEN') and settings.TELEGRAM_BOT_TOKEN:
        print("✅ Telegram bot token is configured")
    else:
        print("⚠️  Telegram bot token not configured")
    
    print("🎉 Application startup completed successfully!")
    print("\n📋 Available commands:")
    print("- python manage.py runserver (for local testing)")
    print("- python manage.py shell (for Django shell)")
    print("- python manage.py setup_webhook (to configure Telegram webhook)")
    print("- python manage.py migrate (to run database migrations)")
    print("- python manage.py collectstatic (to collect static files)")

if __name__ == "__main__":
    main()
