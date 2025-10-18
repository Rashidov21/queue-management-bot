#!/usr/bin/env python3
"""
Deployment script for PythonAnywhere
This script helps with the initial setup and deployment process
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
        sys.exit(1)

def check_environment():
    """Check if we're in the right environment"""
    print("🔍 Checking environment...")
    
    # Check if we're in the project directory
    if not Path("manage.py").exists():
        print("❌ manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected. It's recommended to use a virtual environment.")
    
    print("✅ Environment check passed")

def install_dependencies():
    """Install Python dependencies"""
    run_command("pip install -r requirements.txt", "Installing dependencies")

def setup_database():
    """Set up the database"""
    run_command("python manage.py migrate", "Running database migrations")
    
    # Create superuser if it doesn't exist
    print("🔍 Checking for superuser...")
    try:
        result = subprocess.run(
            "python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser found')\"",
            shell=True, capture_output=True, text=True
        )
        if "No superuser found" in result.stdout:
            print("👤 Creating superuser...")
            subprocess.run("python manage.py createsuperuser", shell=True)
    except:
        print("⚠️  Could not check/create superuser. You may need to create one manually.")

def collect_static():
    """Collect static files"""
    run_command("python manage.py collectstatic --noinput", "Collecting static files")

def create_sample_data():
    """Create sample data for testing"""
    print("📊 Creating sample data...")
    try:
        run_command("python manage.py create_sample_data", "Creating sample data")
    except:
        print("⚠️  Sample data creation failed or command not found")

def setup_environment_file():
    """Set up environment file"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("✅ .env file created. Please update it with your actual values.")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No environment file found. Please create one manually.")

def main():
    """Main deployment function"""
    print("🚀 Starting deployment process...")
    
    check_environment()
    setup_environment_file()
    install_dependencies()
    setup_database()
    collect_static()
    create_sample_data()
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your .env file with actual values")
    print("2. Configure your PythonAnywhere web app")
    print("3. Set up your domain and SSL")
    print("4. Configure your Telegram bot webhook")
    print("\n🔗 Useful commands:")
    print("- python manage.py runserver (for local testing)")
    print("- python manage.py shell (for Django shell)")
    print("- python manage.py createsuperuser (to create admin user)")

if __name__ == "__main__":
    main()
