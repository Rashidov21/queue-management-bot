#!/usr/bin/env python3
"""
Telegram Bot Runner
Starts the Telegram bot
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    """Start Telegram bot"""
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("[STARTUP] Starting Telegram Queue Management Bot...")
    print("[INFO] Bot will respond to messages on Telegram")
    print("[INFO] Make sure Django server is running on port 8001")
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
        # Start Telegram bot
        subprocess.run([
            python_executable, 'telegram_bot.py'
        ], check=True)
    except KeyboardInterrupt:
        print("\n[STOP] Telegram bot stopped")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error starting Telegram bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
