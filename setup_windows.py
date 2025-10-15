#!/usr/bin/env python3
"""
Windows-compatible setup script for Queue Management Bot
"""

import os
import sys
import asyncio
from pathlib import Path


async def setup_database():
    """Initialize database and seed initial data"""
    print("Setting up database...")
    
    try:
        # Import and run database initialization
        from database.db import init_db
        from database.seed import main as seed_main
        
        await init_db()
        print("Database tables created")
        
        await seed_main()
        print("Initial data seeded")
        
    except Exception as e:
        print(f"Database setup failed: {e}")
        return False
    
    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    
    if env_file.exists():
        print(".env file already exists")
        return True
    
    print("Creating .env file...")
    
    # Create .env file with Windows-compatible defaults
    env_content = """# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Database Configuration (SQLite for Windows compatibility)
DATABASE_URL=sqlite+aiosqlite:///./queue_bot.db

# Web Configuration
WEB_HOST=0.0.0.0
WEB_PORT=8000
SECRET_KEY=your-secret-key-change-in-production

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Notification Configuration
REMINDER_HOURS_BEFORE=1
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(".env file created")
    print("Please edit .env file and add your bot token!")
    return True


def check_requirements():
    """Check if all requirements are installed"""
    print("Checking requirements...")
    
    try:
        import aiogram
        import fastapi
        import sqlalchemy
        import apscheduler
        import aiosqlite
        print("All required packages are installed")
        return True
    except ImportError as e:
        print(f"Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


async def main():
    """Main setup function"""
    print("""
========================================
   Queue Management Bot - Windows Setup
========================================

This script will set up your bot environment:
• Check requirements
• Create configuration files
• Initialize SQLite database
• Seed initial data
========================================
    """)
    
    # Check requirements
    if not check_requirements():
        print("\nInstalling requirements...")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Setup database
    if not await setup_database():
        sys.exit(1)
    
    print("""
Windows setup completed successfully!

Next steps:
1. Edit .env file and add your bot token from @BotFather
2. Run the bot: python run.py

For help, run: python run.py help

Note: This setup uses SQLite database for Windows compatibility.
No additional database server is required!
    """)


if __name__ == "__main__":
    asyncio.run(main())
