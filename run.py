#!/usr/bin/env python3
"""
Simple local development runner
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main function to run the Django development server"""
    print("🚀 Starting Queue Management Bot (Local Development)")
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
    
    print("\n📋 Server will be available at:")
    print("🌐 http://localhost:8000")
    print("🌐 http://127.0.0.1:8000")
    print("\n📋 Available endpoints:")
    print("🔹 Home: http://localhost:8000/")
    print("🔹 Admin: http://localhost:8000/admin/")
    print("🔹 API: http://localhost:8000/api/")
    print("🔹 Webhook: http://localhost:8000/webhook/")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the Django development server
        subprocess.run([
            sys.executable, "manage.py", "runserver", "0.0.0.0:8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("\n💡 Try running these commands manually:")
        print("1. pip install -r requirements.txt")
        print("2. python manage.py migrate")
        print("3. python manage.py runserver")

if __name__ == "__main__":
    main()
