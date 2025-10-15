#!/usr/bin/env python3
"""
Simple Queue Management Bot Runner (Windows compatible)
"""

import asyncio
import uvicorn
import logging
from multiprocessing import Process
import os
import sys

from simple_config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_bot():
    """Run the Telegram bot (simplified version)"""
    try:
        logger.info("Starting Telegram bot...")
        print("Bot functionality will be available after full implementation")
        print("For now, you can test the web admin dashboard")
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")


def run_web():
    """Run the web admin dashboard"""
    try:
        logger.info("Starting web admin dashboard...")
        uvicorn.run(
            "web.main:app",
            host=settings.WEB_HOST,
            port=settings.WEB_PORT,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Web server stopped by user")
    except Exception as e:
        logger.error(f"Web server error: {e}")


def main():
    """Main function to run services"""
    print("""
========================================
        Queue Management Bot
========================================

This application runs:
• Telegram Bot (simplified)
• Web Admin Dashboard (full)

Web Dashboard: http://localhost:8000
Bot Token: Configured in .env file
========================================
    """)
    
    # Check if bot token is configured
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "your_telegram_bot_token_here":
        print("ERROR: Bot token not configured!")
        print("Please set BOT_TOKEN in your .env file or environment variables.")
        print("Get your bot token from @BotFather on Telegram.")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "bot":
            run_bot()
        elif mode == "web":
            run_web()
        elif mode == "help":
            print("""
Usage: python simple_run.py [mode]

Modes:
  bot    - Run only the Telegram bot (simplified)
  web    - Run only the web admin dashboard
  help   - Show this help message
  (none) - Run both bot and web dashboard

Examples:
  python simple_run.py bot
  python simple_run.py web
  python simple_run.py
            """)
        else:
            print(f"Unknown mode: {mode}")
            print("Use 'python simple_run.py help' for usage information.")
    else:
        # Run both services
        print("Starting both services...")
        
        # Start bot in a separate process
        bot_process = Process(target=run_bot)
        bot_process.start()
        
        # Start web server in a separate process
        web_process = Process(target=run_web)
        web_process.start()
        
        try:
            # Wait for both processes
            bot_process.join()
            web_process.join()
        except KeyboardInterrupt:
            print("\nShutting down services...")
            bot_process.terminate()
            web_process.terminate()
            bot_process.join()
            web_process.join()
            print("Services stopped")


if __name__ == "__main__":
    main()
