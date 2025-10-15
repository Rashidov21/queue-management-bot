#!/usr/bin/env python3
"""
Django Server Runner
Starts the Django development server
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start Django development server"""
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queue_management.settings')
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🚀 Starting Django Queue Management System...")
    print("📊 Admin Panel: http://localhost:8001/admin/")
    print("🔗 API Endpoints: http://localhost:8001/api/")
    print("👤 Admin Login: admin / admin123")
    print("\n" + "="*50)
    
    try:
        # Start Django development server
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '8001'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Django server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Django server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
