#!/usr/bin/env python3
"""
Django Server Runner
Starts the Django development server
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    """Start Django development server"""
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queue_management.settings')
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("[STARTUP] Starting Django Queue Management System...")
    print("[INFO] Admin Panel: http://localhost:8001/admin/")
    print("[INFO] API Endpoints: http://localhost:8001/api/")
    print("[INFO] Admin Login: admin / admin123")
    print("\n" + "="*50)
    
    # Use virtual environment Python if available
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python.exe"
    else:
        python_cmd = "venv/bin/python"
    
    # Check if virtual environment exists
    if Path("venv").exists() and Path(python_cmd).exists():
        python_executable = python_cmd
        print("[INFO] Using virtual environment Python")
    else:
        python_executable = sys.executable
        print("[INFO] Using system Python")
    
    try:
        # Start Django development server
        subprocess.run([
            python_executable, 'manage.py', 'runserver', '8001'
        ], check=True)
    except KeyboardInterrupt:
        print("\n[STOP] Django server stopped")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error starting Django server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
