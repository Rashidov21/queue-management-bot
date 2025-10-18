#!/usr/bin/env python3
"""
Simple setup script for local development
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
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Queue Management Bot for Local Development")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ manage.py not found. Please run this script from the project root.")
        return
    
    print("✅ Project directory found")
    
    # Create necessary directories
    directories = ['static', 'media']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        return
    
    # Run database migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        print("❌ Failed to run migrations. Please check your database configuration.")
        return
    
    # Create superuser
    print("\n👤 Creating superuser (admin user)...")
    print("You'll need to enter username, email, and password for the admin user.")
    run_command("python manage.py createsuperuser", "Creating superuser")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python run.py")
    print("2. Visit: http://localhost:8000")
    print("3. Admin panel: http://localhost:8000/admin/")
    print("\n🔧 Useful commands:")
    print("- python run.py (start development server)")
    print("- python manage.py shell (Django shell)")
    print("- python manage.py createsuperuser (create admin user)")

if __name__ == "__main__":
    main()