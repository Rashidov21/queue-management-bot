#!/usr/bin/env python3
"""
Setup script for Queue Management Bot
"""

import os
import sys
import asyncio
from pathlib import Path


async def setup_database():
    """Initialize database and seed initial data"""
    print("🗄️ Setting up database...")
    
    try:
        # Import and run database initialization
        from database.db import init_db
        from database.seed import main as seed_main
        
        await init_db()
        print("✅ Database tables created")
        
        await seed_main()
        print("✅ Initial data seeded")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    # Copy from example
    example_file = Path("env.example")
    if example_file.exists():
        with open(example_file, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created from template")
        print("⚠️  Please edit .env file and add your bot token!")
        return True
    else:
        print("❌ env.example file not found")
        return False


def check_requirements():
    """Check if all requirements are installed"""
    print("📦 Checking requirements...")
    
    try:
        import aiogram
        import fastapi
        import sqlalchemy
        import apscheduler
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


async def main():
    """Main setup function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🤖 Queue Management Bot Setup                ║
║                                                              ║
║  This script will set up your bot environment:              ║
║  • Check requirements                                        ║
║  • Create configuration files                                ║
║  • Initialize database                                       ║
║  • Seed initial data                                         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Setup database
    if not await setup_database():
        sys.exit(1)
    
    print("""
🎉 Setup completed successfully!

Next steps:
1. Edit .env file and add your bot token from @BotFather
2. Run the bot: python run.py

For help, run: python run.py help
    """)


if __name__ == "__main__":
    asyncio.run(main())
