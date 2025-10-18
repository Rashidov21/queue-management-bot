#!/usr/bin/env python3
"""
Debug script for PythonAnywhere deployment
Run this to diagnose common issues
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check environment variables and paths"""
    print("🔍 Checking environment...")
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check if we're in the right place
    if not Path("manage.py").exists():
        print("❌ manage.py not found. Please run this from the project root.")
        return False
    
    print("✅ manage.py found")
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import django
        print(f"✅ Django {django.get_version()} found")
    except ImportError:
        print("❌ Django not found. Run: pip3.10 install --user -r requirements.txt")
        return False
    
    try:
        import rest_framework
        print("✅ Django REST Framework found")
    except ImportError:
        print("❌ Django REST Framework not found")
        return False
    
    try:
        import corsheaders
        print("✅ Django CORS Headers found")
    except ImportError:
        print("❌ Django CORS Headers not found")
        return False
    
    return True

def check_database():
    """Check database configuration"""
    print("🔍 Checking database...")
    
    try:
        import django
        from django.conf import settings
        from django.db import connection
        
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queue_management.settings')
        django.setup()
        
        # Test database connection
        connection.ensure_connection()
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_static_files():
    """Check static files configuration"""
    print("🔍 Checking static files...")
    
    static_dir = Path("staticfiles")
    if static_dir.exists():
        print("✅ staticfiles directory exists")
        return True
    else:
        print("❌ staticfiles directory not found. Run: python3.10 manage.py collectstatic --noinput")
        return False

def check_environment_file():
    """Check environment file"""
    print("🔍 Checking environment file...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        
        # Check for required variables
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = ['SECRET_KEY', 'ALLOWED_HOSTS', 'DEBUG']
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        else:
            print("✅ Required environment variables found")
            
        return True
    else:
        print("❌ .env file not found. Run: cp env.example .env")
        return False

def main():
    """Main diagnostic function"""
    print("🚀 PythonAnywhere Debug Script")
    print("=" * 50)
    
    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("Database", check_database),
        ("Static Files", check_static_files),
        ("Environment File", check_environment_file),
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n📋 {name} Check:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during {name} check: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Your application should be working.")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\n🔧 Quick fixes:")
        print("1. Install dependencies: pip3.10 install --user -r requirements.txt")
        print("2. Run migrations: python3.10 manage.py migrate")
        print("3. Collect static files: python3.10 manage.py collectstatic --noinput")
        print("4. Create .env file: cp env.example .env")
        print("5. Update .env with your values")

if __name__ == "__main__":
    main()
