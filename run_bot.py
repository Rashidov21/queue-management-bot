#!/usr/bin/env python3
"""
Telegram Bot Runner
Starts the Telegram bot
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start Telegram bot"""
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🤖 Starting Telegram Queue Management Bot...")
    print("📱 Bot will respond to messages on Telegram")
    print("🔗 Make sure Django server is running on port 8001")
    print("\n" + "="*50)
    
    try:
        # Start Telegram bot
        subprocess.run([
            sys.executable, 'telegram_bot.py'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Telegram bot stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Telegram bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
