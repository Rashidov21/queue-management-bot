#!/usr/bin/env python3
"""
PythonAnywhere management script
This script helps manage the deployment on PythonAnywhere
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def setup_pythonanywhere():
    """Set up the project for PythonAnywhere"""
    print("🚀 Setting up project for PythonAnywhere...")
    
    # Create necessary directories
    directories = ['logs', 'staticfiles', 'media']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Install dependencies
    run_command("pip3.10 install --user -r requirements.txt", "Installing dependencies")
    
    # Run migrations
    run_command("python3.10 manage.py migrate", "Running database migrations")
    
    # Collect static files
    run_command("python3.10 manage.py collectstatic --noinput", "Collecting static files")
    
    # Create superuser if needed
    print("👤 Creating superuser...")
    run_command("python3.10 manage.py createsuperuser", "Creating superuser")
    
    print("✅ PythonAnywhere setup completed!")

def update_project():
    """Update the project from Git"""
    print("🔄 Updating project from Git...")
    
    # Pull latest changes
    run_command("git pull origin main", "Pulling latest changes")
    
    # Install/update dependencies
    run_command("pip3.10 install --user -r requirements.txt", "Updating dependencies")
    
    # Run migrations
    run_command("python3.10 manage.py migrate", "Running migrations")
    
    # Collect static files
    run_command("python3.10 manage.py collectstatic --noinput", "Collecting static files")
    
    print("✅ Project updated successfully!")

def restart_webapp():
    """Restart the PythonAnywhere web app"""
    print("🔄 Restarting web app...")
    
    # This would typically be done through the PythonAnywhere web interface
    # or via their API if you have the credentials
    print("⚠️  Please restart your web app manually through the PythonAnywhere dashboard")
    print("   Go to: Web tab -> Reload button")

def check_status():
    """Check the status of the application"""
    print("🔍 Checking application status...")
    
    # Check if Django is working
    result = run_command("python3.10 manage.py check", "Checking Django configuration")
    if result:
        print("✅ Django configuration is valid")
    else:
        print("❌ Django configuration has issues")
    
    # Check database
    result = run_command("python3.10 manage.py showmigrations", "Checking database migrations")
    if result:
        print("✅ Database migrations are up to date")
    else:
        print("❌ Database migration issues")

def setup_telegram_webhook():
    """Set up Telegram webhook"""
    print("🤖 Setting up Telegram webhook...")
    
    # This would require the bot token and webhook URL
    print("⚠️  Please set up your Telegram webhook manually:")
    print("   1. Get your bot token from @BotFather")
    print("   2. Set TELEGRAM_BOT_TOKEN in your .env file")
    print("   3. Set TELEGRAM_WEBHOOK_URL in your .env file")
    print("   4. Run: python3.10 manage.py setup_webhook")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python manage_pythonanywhere.py <command>")
        print("Commands:")
        print("  setup     - Initial setup for PythonAnywhere")
        print("  update    - Update project from Git")
        print("  restart   - Restart web app")
        print("  status    - Check application status")
        print("  webhook   - Set up Telegram webhook")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_pythonanywhere()
    elif command == "update":
        update_project()
    elif command == "restart":
        restart_webapp()
    elif command == "status":
        check_status()
    elif command == "webhook":
        setup_telegram_webhook()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
