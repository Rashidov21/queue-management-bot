#!/usr/bin/env python3
"""
Telegram Bot for Queue Management System
Integrates with Django REST API
"""

import asyncio
import logging
import os
import sys
import subprocess
import threading
import platform
from datetime import date, time, timedelta
from typing import Dict, List
from pathlib import Path

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8001/api')

if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables")
    sys.exit(1)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Removed unused state classes - now using web app only


# Helper functions for API calls
async def make_api_request(method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
    """Make HTTP request to Django API"""
    url = f"{API_BASE_URL}{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        try:
            if method.upper() == 'GET':
                async with session.get(url, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'POST':
                async with session.post(url, json=data, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'PUT':
                async with session.put(url, json=data, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'DELETE':
                async with session.delete(url, headers=headers) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}


async def get_or_create_user(telegram_id: int, username: str) -> Dict:
    """Get or create user via API"""
    # For MVP, we'll create a simple user without authentication
    # In production, you'd implement proper authentication
    return {
        "id": telegram_id,
        "username": username,
        "telegram_id": telegram_id,
        "role": "client"
    }


async def register_user_in_django(telegram_user):
    """Register user in Django project using Telegram data"""
    try:
        # Prepare user data from Telegram
        user_data = {
            "username": telegram_user.username or f"user_{telegram_user.id}",
            "first_name": telegram_user.first_name or "",
            "last_name": telegram_user.last_name or "",
            "telegram_id": telegram_user.id,
            "telegram_username": telegram_user.username or "",
            "role": "client"
        }
        
        # Register user via API
        response = await make_api_request('POST', '/users/register/', user_data)
        
        if 'error' not in response:
            logger.info(f"User {telegram_user.id} registered successfully")
        else:
            logger.info(f"User {telegram_user.id} already exists or registration failed")
            
    except Exception as e:
        logger.error(f"Error registering user {telegram_user.id}: {e}")


# Command handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Start command handler"""
    await state.clear()
    
    # Register user in Django project
    await register_user_in_django(message.from_user)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ Yordam va ma'lumot")],
            [KeyboardButton(text="🌐 Web ilovasini ochish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await message.answer(
        f"👋 Salom {message.from_user.first_name}!\n\n"
        f"Navbatni boshqarish botiga xush kelibsiz! 🚀\n\n"
        f"To'liq funksionallik uchun web ilovasini ishlatishingiz mumkin.\n\n"
        f"Quyidagi tugmalardan birini tanlang:",
        reply_markup=keyboard
    )


# Removed old service handlers - now using web app only


# Removed old callback handlers - now using web app only


# Removed all old booking flow handlers - now using web app only




@dp.message(lambda message: message.text == "🌐 Web ilovasini ochish")
async def show_web_app(message: types.Message):
    """Open web application"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Web ilovasini ochish", url=f"http://localhost:8001/users/telegram-login/?telegram_id={message.from_user.id}")]
    ])
    
    await message.answer(
        "🌐 **Web ilovasini ochish**\n\n"
        "To'liq funksionallik uchun web ilovasini ishlatishingiz mumkin.\n\n"
        "Quyidagi tugmani bosing:",
        reply_markup=keyboard
    )


@dp.message(lambda message: message.text == "ℹ️ Yordam va ma'lumot")
async def show_help(message: types.Message):
    """Show help and system information"""
    await message.answer(
        "ℹ️ **Yordam va tizim ma'lumotlari**\n\n"
        "🤖 **Bot haqida:**\n"
        "Bu bot navbatni boshqarish tizimi uchun yaratilgan. "
        "To'liq funksionallik uchun web ilovasini ishlatishingiz kerak.\n\n"
        "📋 **Mavjud buyruqlar:**\n"
        "• /start - Asosiy menyu\n"
        "• ℹ️ Yordam va ma'lumot - Bu yordamni ko'rsatish\n"
        "• 🌐 Web ilovasini ochish - Web ilovasini ochish\n\n"
        "🌐 **Web ilovasi:**\n"
        "To'liq funksionallik uchun 'Web ilovasini ochish' tugmasini ishlating\n"
        "URL: http://localhost:8001\n\n"
        "🔧 **Tizim ma'lumotlari:**\n"
        "• Bot versiyasi: 1.0.0\n"
        "• Web ilova: Django 5.2.1\n"
        "• Ma'lumotlar bazasi: SQLite\n"
        "• Server: Localhost:8001\n\n"
        "📞 **Qo'llab-quvvatlash:**\n"
        "Agar yordamga muhtoj bo'lsangiz, administratorga murojaat qiling.\n\n"
        "Asosiy menyuga qaytish uchun /start buyrug'ini ishlating."
    )


@dp.message()
async def handle_unknown_message(message: types.Message):
    """Handle unknown messages"""
    await message.answer(
        "❓ Men bu buyruqni tushunmayman.\n\n"
        "Asosiy menyuni ko'rish uchun /start buyrug'ini ishlating.\n\n"
        "Yordam uchun 'ℹ️ Yordam va ma'lumot' tugmasini bosing."
    )


def start_django_server():
    """Start Django development server in a separate thread"""
    try:
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queue_management.settings')
        
        # Change to project directory
        project_dir = Path(__file__).parent
        os.chdir(project_dir)
        
        logger.info("Starting Django web server on port 8001...")
        
        # Use virtual environment Python if available
        if platform.system() == "Windows":
            python_cmd = "venv\\Scripts\\python.exe"
        else:
            python_cmd = "venv/bin/python"
        
        # Check if virtual environment exists
        if Path("venv").exists() and Path(python_cmd).exists():
            python_executable = python_cmd
        else:
            python_executable = sys.executable
        
        # Start Django development server
        subprocess.run([
            python_executable, 'manage.py', 'runserver', '8001'
        ], check=True)
    except Exception as e:
        logger.error(f"Error starting Django server: {e}")


async def main():
    """Main function to start the bot and web server"""
    logger.info("Starting Queue Management System...")
    logger.info("Starting Django web server...")
    
    # Start Django server in a separate thread
    django_thread = threading.Thread(target=start_django_server, daemon=True)
    django_thread.start()
    
    # Give Django server time to start
    await asyncio.sleep(3)
    
    logger.info("Django web server started at http://localhost:8001")
    logger.info("Telegram bot ishga tushmoqda...")
    
    # Delete webhook if it exists
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi")
    except Exception as e:
        logger.error(f"Bot xatosi: {e}")
        sys.exit(1)
