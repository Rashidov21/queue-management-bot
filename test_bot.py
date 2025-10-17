#!/usr/bin/env python3
"""
Test script for the simplified Telegram bot
"""

import asyncio
import logging
from telegram_bot import bot, dp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_bot():
    """Test the bot functionality"""
    logger.info("Testing simplified Telegram bot...")
    
    # Test bot token
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot connected successfully: @{bot_info.username}")
        logger.info(f"Bot name: {bot_info.first_name}")
        logger.info(f"Bot ID: {bot_info.id}")
    except Exception as e:
        logger.error(f"Failed to connect to bot: {e}")
        return False
    
    logger.info("Bot test completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_bot())
