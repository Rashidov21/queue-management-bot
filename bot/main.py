from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncio
import logging

from config import settings
from database.db import init_db
from bot.handlers import start, provider, client
from scheduler import scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Include routers
dp.include_router(start.router)
dp.include_router(provider.router)
dp.include_router(client.router)


async def on_startup():
    """Bot startup function"""
    logger.info("🚀 Starting bot...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Set up scheduler
    scheduler.set_bot(bot)
    scheduler.start()
    logger.info("✅ Scheduler started")
    
    # Set webhook if configured
    if settings.WEBHOOK_URL:
        webhook_url = f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        logger.info(f"✅ Webhook set: {webhook_url}")
    else:
        # Delete webhook if running in polling mode
        await bot.delete_webhook()
        logger.info("✅ Webhook deleted, running in polling mode")


async def on_shutdown():
    """Bot shutdown function"""
    logger.info("🛑 Shutting down bot...")
    
    # Stop scheduler
    scheduler.stop()
    logger.info("✅ Scheduler stopped")
    
    # Delete webhook
    await bot.delete_webhook()
    logger.info("✅ Webhook deleted")


async def create_webhook_app():
    """Create aiohttp application for webhook"""
    app = web.Application()
    
    # Create webhook handler
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.SECRET_KEY
    )
    
    # Register webhook handler
    webhook_handler.register(app, path=settings.WEBHOOK_PATH)
    
    # Setup application
    setup_application(app, dp, bot=bot)
    
    return app


async def run_polling():
    """Run bot in polling mode"""
    await on_startup()
    
    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during polling: {e}")
    finally:
        await on_shutdown()


async def run_webhook():
    """Run bot with webhook"""
    await on_startup()
    
    try:
        # Create webhook app
        app = await create_webhook_app()
        
        # Start webhook server
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        
        logger.info("✅ Webhook server started on port 8080")
        
        # Keep running
        while True:
            await asyncio.sleep(3600)
            
    except Exception as e:
        logger.error(f"Error during webhook: {e}")
    finally:
        await on_shutdown()


if __name__ == "__main__":
    # Choose mode based on webhook configuration
    if settings.WEBHOOK_URL:
        asyncio.run(run_webhook())
    else:
        asyncio.run(run_polling())
