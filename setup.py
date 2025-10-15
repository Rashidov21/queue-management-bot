#!/usr/bin/env python3
"""
Setup script for Queue Management Bot
Creates virtual environment and installs dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[SETUP] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("[STARTUP] Setting up Queue Management Bot...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ is required. Current version:", sys.version)
        sys.exit(1)
    
    print(f"[OK] Python version: {sys.version}")
    
    # Create virtual environment
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("[OK] Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Run Django migrations
    if not run_command(f"{python_cmd} manage.py migrate", "Running Django migrations"):
        sys.exit(1)
    
    # Create superuser
    print("[SETUP] Creating admin user...")
    try:
        subprocess.run([
            python_cmd, "manage.py", "shell", "-c",
            "from django.contrib.auth import get_user_model; "
            "User = get_user_model(); "
            "admin, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}); "
            "admin.set_password('admin123'); "
            "admin.save(); "
            "print('Admin user created successfully' if created else 'Admin user already exists')"
        ], check=True)
        print("[OK] Admin user created (admin / admin123)")
    except subprocess.CalledProcessError:
        print("[WARNING] Could not create admin user automatically. You can create it manually later.")
    
    # Create sample data
    if not run_command(f"{python_cmd} manage.py create_sample_data", "Creating sample data"):
        print("[WARNING] Could not create sample data. You can create it manually later.")
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Setup completed successfully!")
    print("\n[INFO] Next steps:")
    print("1. Copy env.example to .env and configure your settings")
    print("2. Start Django server: python run_django.py")
    print("3. Start Telegram bot: python run_bot.py")
    print("\n[INFO] Access points:")
    print("- Django Admin: http://localhost:8001/admin/")
    print("- API: http://localhost:8001/api/")
    print("- Admin login: admin / admin123")
    print("\n[INFO] Documentation: README.md")

if __name__ == "__main__":
    main()
